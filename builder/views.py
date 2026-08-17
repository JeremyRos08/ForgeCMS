import json
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import BuilderSnapshot, CustomContentType, CustomField
from .project_generator import GeneratedCMSProjectGenerator
from .schema_engine import SchemaEngine


@login_required
def builder_dashboard(request):
    types = list(CustomContentType.objects.prefetch_related('fields').order_by('name'))
    snapshots = BuilderSnapshot.objects.select_related('created_by')[:20]
    layout_seed = {
        content_type.id: (
            (content_type.config or {}).get('layout', {'blocks': []})
            if isinstance(content_type.config, dict)
            else {'blocks': []}
        )
        for content_type in types
    }
    return render(
        request,
        'builder/dashboard.html',
        {
            'types': types,
            'snapshots': snapshots,
            'layout_seed': layout_seed,
        },
    )


@login_required
def export_schema(request):
    schema = SchemaEngine().export_schema()
    return JsonResponse(schema, json_dumps_params={'indent': 2, 'ensure_ascii': False})


def _parse_json_body(request):
    try:
        return json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def _require_builder_admin(user):
    return bool(user.is_superuser or user.is_staff)


@login_required
@require_POST
def save_type_config(request, type_id):
    if not _require_builder_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Acces refuse.'}, status=403)

    content_type = get_object_or_404(CustomContentType, id=type_id)
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'JSON invalide.'}, status=400)

    config = payload.get('config')
    if not isinstance(config, dict):
        return JsonResponse({'ok': False, 'error': 'config doit etre un objet JSON.'}, status=400)

    content_type.config = config
    content_type.save(update_fields=['config', 'updated_at'])
    return JsonResponse({'ok': True, 'message': 'Configuration du type enregistree.'})


@login_required
@require_POST
def save_field_config(request, field_id):
    if not _require_builder_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Acces refuse.'}, status=403)

    field = get_object_or_404(CustomField, id=field_id)
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'JSON invalide.'}, status=400)

    config = payload.get('config')
    if not isinstance(config, dict):
        return JsonResponse({'ok': False, 'error': 'config doit etre un objet JSON.'}, status=400)

    field.config = config
    field.save(update_fields=['config'])
    return JsonResponse({'ok': True, 'message': 'Configuration du champ enregistree.'})


@login_required
@require_POST
def reorder_fields(request, type_id):
    if not _require_builder_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Acces refuse.'}, status=403)

    content_type = get_object_or_404(CustomContentType, id=type_id)
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'JSON invalide.'}, status=400)

    ordered_ids = payload.get('ordered_ids')
    if not isinstance(ordered_ids, list):
        return JsonResponse({'ok': False, 'error': 'ordered_ids doit etre une liste.'}, status=400)

    type_field_ids = list(content_type.fields.values_list('id', flat=True))
    if sorted(ordered_ids) != sorted(type_field_ids):
        return JsonResponse(
            {'ok': False, 'error': 'La liste des champs ne correspond pas au type.'},
            status=400,
        )

    field_by_id = {field.id: field for field in content_type.fields.all()}
    with transaction.atomic():
        for index, field_id in enumerate(ordered_ids):
            field = field_by_id[field_id]
            if field.order != index:
                field.order = index
                field.save(update_fields=['order'])

    return JsonResponse({'ok': True, 'message': 'Ordre des champs mis a jour.'})


@login_required
@require_POST
def save_type_layout(request, type_id):
    if not _require_builder_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Acces refuse.'}, status=403)

    content_type = get_object_or_404(CustomContentType, id=type_id)
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'JSON invalide.'}, status=400)

    layout = payload.get('layout')
    if not isinstance(layout, dict):
        return JsonResponse({'ok': False, 'error': 'layout doit etre un objet JSON.'}, status=400)

    blocks = layout.get('blocks', [])
    if not isinstance(blocks, list):
        return JsonResponse({'ok': False, 'error': 'layout.blocks doit etre une liste.'}, status=400)

    normalized_blocks = []
    for index, block in enumerate(blocks):
        if not isinstance(block, dict):
            continue
        block_type = str(block.get('type', 'text')).strip() or 'text'
        block_label = str(block.get('label', f'Block {index + 1}')).strip() or f'Block {index + 1}'
        block_id = str(block.get('id', f'block-{index + 1}')).strip() or f'block-{index + 1}'
        block_config = block.get('config') if isinstance(block.get('config'), dict) else {}
        normalized_blocks.append(
            {
                'id': block_id,
                'type': block_type,
                'label': block_label,
                'config': block_config,
            }
        )

    updated_config = dict(content_type.config or {})
    updated_config['layout'] = {'blocks': normalized_blocks}
    content_type.config = updated_config
    content_type.save(update_fields=['config', 'updated_at'])

    return JsonResponse({'ok': True, 'message': 'Layout sauvegarde.', 'layout': updated_config['layout']})


@login_required
@require_POST
def create_snapshot(request):
    if not _require_builder_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Acces refuse.'}, status=403)

    payload = _parse_json_body(request) or {}
    note = payload.get('note', '')
    note = str(note).strip()[:255]

    engine = SchemaEngine()
    snapshot = engine.create_snapshot(user=request.user, note=note, is_auto=False)
    return JsonResponse({'ok': True, 'message': 'Snapshot cree.', 'snapshot_id': snapshot.id, 'name': snapshot.name})


@login_required
@require_POST
def rollback_snapshot(request, snapshot_id):
    if not _require_builder_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Acces refuse.'}, status=403)

    snapshot = get_object_or_404(BuilderSnapshot, id=snapshot_id)
    engine = SchemaEngine()

    try:
        engine.apply_snapshot(snapshot)
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=400)

    return JsonResponse({'ok': True, 'message': f'Rollback applique depuis snapshot #{snapshot.id}.'})


@login_required
@require_POST
def generate_project(request):
    if not _require_builder_admin(request.user):
        return JsonResponse({'ok': False, 'error': 'Acces refuse.'}, status=403)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'ok': False, 'error': 'JSON invalide.'}, status=400)

    project_name = str(payload.get('project_name', 'Forge Generated CMS')).strip() or 'Forge Generated CMS'
    project_slug = str(payload.get('project_slug', 'forge_generated_cms')).strip() or 'forge_generated_cms'
    output_name = str(payload.get('output_name', '')).strip() or project_slug

    safe_output_name = re.sub(r'[^a-zA-Z0-9_-]+', '-', output_name).strip('-').lower()
    if not safe_output_name:
        return JsonResponse({'ok': False, 'error': 'Nom de dossier invalide.'}, status=400)

    output_dir = Path(settings.BASE_DIR) / 'generated' / safe_output_name
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    if output_dir.exists() and any(output_dir.iterdir()):
        return JsonResponse(
            {'ok': False, 'error': f'Dossier non vide: {output_dir}. Choisis un autre nom.'},
            status=400,
        )

    schema = SchemaEngine().export_schema()
    generator = GeneratedCMSProjectGenerator(
        schema=schema,
        output_dir=output_dir,
        project_slug=project_slug,
        project_name=project_name,
    )
    created_files = generator.generate()
    return JsonResponse(
        {
            'ok': True,
            'message': 'Projet genere.',
            'output_dir': str(output_dir),
            'files_created': len(created_files),
        }
    )
