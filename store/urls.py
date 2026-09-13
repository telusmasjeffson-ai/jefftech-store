from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('panier/', views.voir_panier, name='panier'), # Nou mete name='panier' isit la
    path('panier/', views.voir_panier, name='voir_panier'), # Support pou 'voir_panier' tou
    path('ajouter-au-panier/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('diminuer/<int:produit_id>/', views.diminuer_quantite, name='diminuer_quantite'),
    path('supprimer/<int:produit_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    
    # Lòt wout yo
    path('paiement/', views.paiement, name='paiement'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion_user, name='connexion'),
    path('deconnexion/', views.deconnexion_user, name='deconnexion'),
    path('apropos/', views.apropos, name='apropos'),
    path('categories/', views.categories, name='categories'),
    path('recherche/', views.recherche, name='recherche'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    path('panier/', views.voir_panier, name='panier'),
    path('panier/', views.voir_panier, name='voir_panier'),
    path('admin-dashboard/commandes/', views.gestion_commandes, name='gestion_commandes'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_panier, name='ajouter_panier'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    path('commander-service/', views.commander_service, name='commander_service'),
]