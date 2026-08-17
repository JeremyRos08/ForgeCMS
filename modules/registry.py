class CMSModule:
    name = ''
    label = ''
    description = ''
    dependencies = []


class BlogModule(CMSModule):
    name = 'blog'
    label = 'Blog'
    description = 'Gestion des articles et catégories'
    dependencies = ['accounts']
