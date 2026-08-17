FIELD_TYPES = [
    ('text', 'Texte'),
    ('textarea', 'Texte long'),
    ('richtext', 'Éditeur riche'),
    ('number', 'Nombre'),
    ('boolean', 'Booléen'),
    ('date', 'Date'),
    ('datetime', 'Date et heure'),
    ('image', 'Image'),
    ('file', 'Fichier'),
    ('relation', 'Relation'),
]

DJANGO_FIELD_MAP = {
    'text': 'models.CharField(max_length=255)',
    'textarea': 'models.TextField()',
    'richtext': 'models.TextField()',
    'number': 'models.DecimalField(max_digits=12, decimal_places=2)',
    'boolean': 'models.BooleanField(default=False)',
    'date': 'models.DateField(null=True, blank=True)',
    'datetime': 'models.DateTimeField(null=True, blank=True)',
    'image': 'models.ImageField(upload_to="generated/images/", blank=True, null=True)',
    'file': 'models.FileField(upload_to="generated/files/", blank=True, null=True)',
    'relation': 'models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)',
}
