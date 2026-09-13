from django.db import models
from django.contrib.auth.models import User


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom


class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class PanierItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    def total_prix(self):
        return self.produit.prix * self.quantite

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"


class Commande(models.Model):
    MOYENS_PAIEMENT = [
        ('natcash', 'Natcash'),
        ('moncash', 'Moncash'),
        ('meru', 'Meru Card'),
        ('binance', 'Binance Pay'),
    ]
    
    STATUTS = [
        ('en_attente', 'En attente de validation'),
        ('approuve', 'Paiement Validé'),
        ('emballe', 'Commande Emballée'),
        ('expedie', 'En cours de Livraison'),
        ('livre', 'Livré avec Succès'),
        ('rejete', 'Commande Rejetée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    moyen_paiement = models.CharField(max_length=20, choices=MOYENS_PAIEMENT)
    whatsapp = models.CharField(max_length=20)
    adresse_livraison = models.TextField(blank=True, null=True, default="Non spécifiée")
    preuve = models.ImageField(upload_to='preuves_paiement/')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_attente')
    date_commande = models.DateTimeField(auto_now_add=True)
    date_mise_a_jour = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.user.username} ({self.get_statut_display()})"


class CommandeItem(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.SET_NULL, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField(default=1)

    def total_ligne(self):
        return self.prix * self.quantite

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom if self.produit else 'Pwodui efase'} pou Kòmand #{self.commande.id}"