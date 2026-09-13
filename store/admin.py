from django.contrib import admin
from django.utils.html import format_html
from .models import Categorie, Produit, PanierItem, Commande


admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(PanierItem)


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'moyen_paiement', 'whatsapp', 'total', 'voir_preuve', 'statut', 'date_commande')
    list_filter = ('statut', 'moyen_paiement')
    list_editable = ('statut',)  # Pou w ka chanje statut an an 1 klik!
    search_fields = ('user__username', 'whatsapp', 'id')

    # Fonksyon pou w ka klike sou prèv la pou ouvè l nan yon lòt onglet
    def voir_preuve(self, obj):
        if obj.preuve:
            return format_html('<a href="{}" target="_blank" style="color: #0d6efd; font-weight: bold;">Gade Prèv</a>', obj.preuve.url)
        return "Pa gen prèv"
    
    voir_preuve.short_description = "Preuve"