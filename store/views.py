import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from .models import Produit, Categorie, Commande, CommandeItem, EmailVerification


def accueil(request):
    produits_recents = Produit.objects.all().order_by('-date_ajout')[:8]
    return render(request, 'store/accueil.html', {'produits': produits_recents})


@login_required(login_url='connexion')
def ajouter_panier(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    panier = request.session.get('panier', {})
    
    p_id = str(produit_id)
    if p_id in panier:
        panier[p_id] += 1
    else:
        panier[p_id] = 1
        
    request.session['panier'] = panier
    return redirect('panier')

ajouter_au_panier = ajouter_panier


@login_required(login_url='connexion')
def voir_panier(request):
    panier = request.session.get('panier', {})
    articles = []
    total_general = 0

    for produit_id, quantite in panier.items():
        try:
            produit = Produit.objects.get(id=produit_id)
            total_article = produit.prix * quantite
            total_general += total_article
            articles.append({
                'produit': produit,
                'quantite': quantite,
                'total': total_article,
            })
        except Produit.DoesNotExist:
            continue

    context = {
        'articles': articles,
        'total_general': total_general,
    }
    return render(request, 'store/panier.html', context)


@login_required(login_url='connexion')
def diminuer_quantite(request, produit_id):
    panier = request.session.get('panier', {})
    p_id = str(produit_id)

    if p_id in panier:
        if panier[p_id] > 1:
            panier[p_id] -= 1
        else:
            del panier[p_id]

    request.session['panier'] = panier
    return redirect('panier')


@login_required(login_url='connexion')
def supprimer_du_panier(request, produit_id):
    panier = request.session.get('panier', {})
    p_id = str(produit_id)

    if p_id in panier:
        del panier[p_id]

    request.session['panier'] = panier
    return redirect('panier')


@login_required(login_url='connexion')
def paiement(request):
    panier = request.session.get('panier', {})
    articles = []
    total_general = 0

    for produit_id, quantite in panier.items():
        try:
            produit = Produit.objects.get(id=produit_id)
            total_article = produit.prix * quantite
            total_general += total_article
            articles.append({
                'produit': produit,
                'quantite': quantite,
                'total': total_article,
            })
        except Produit.DoesNotExist:
            continue

    if not articles:
        return redirect('panier')

    if request.method == 'POST':
        moyen_paiement = request.POST.get('moyen_paiement')
        whatsapp = request.POST.get('whatsapp')
        adresse_livraison = request.POST.get('adresse_livraison', 'Non spécifiée')
        preuve = request.FILES.get('preuve')

        if moyen_paiement and whatsapp and preuve:
            commande = Commande.objects.create(
                user=request.user,
                moyen_paiement=moyen_paiement,
                whatsapp=whatsapp,
                adresse_livraison=adresse_livraison,
                preuve=preuve,
                total=total_general,
                statut='en_attente'
            )

            for item in articles:
                CommandeItem.objects.create(
                    commande=commande,
                    produit=item['produit'],
                    prix=item['produit'].prix,
                    quantite=item['quantite']
                )

            request.session['panier'] = {}
            return render(request, 'store/confirmation.html')

    context = {
        'articles': articles,
        'total_general': total_general,
    }
    return render(request, 'store/paiement.html', context)


@login_required(login_url='connexion')
def commander_service(request):
    if request.method == 'POST':
        type_service = request.POST.get('type_service', 'service')
        identifiant = request.POST.get('meru_tag') or request.POST.get('identifiant', '')
        whatsapp = request.POST.get('whatsapp')
        montant = request.POST.get('montant_usd') or request.POST.get('montant', '0')
        moyen_paiement = request.POST.get('moyen_paiement')
        preuve = request.FILES.get('preuve')

        if whatsapp and moyen_paiement and preuve:
            description_complete = f"Sèvis: {type_service} | ID/Info: {identifiant}"
            
            Commande.objects.create(
                user=request.user,
                moyen_paiement=moyen_paiement,
                whatsapp=whatsapp,
                adresse_livraison=description_complete,
                preuve=preuve,
                total=montant,
                statut='en_attente'
            )
            return redirect('mes_commandes')
            
    return redirect('accueil')


def inscription(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Inaktif jiskaske l mete kòd verifikasyon an
            user.save()

            # Jenere epi sove kòd verifikasyon 6 chif la
            verification, created = EmailVerification.objects.get_or_create(user=user)
            verification.code = str(random.randint(100000, 999999))
            verification.save()

            # Voye imèl la
            send_mail(
                'Kòd Verifikasyon Kont JeffTech Ou',
                f'Bonjou {user.username},\n\nKòd verifikasyon ou an se: {verification.code}\n\nAntre kòd sa a sou sit la pou aktive kont ou.',
                None,
                [user.email],
                fail_silently=False,
            )

            request.session['verify_user_id'] = user.id
            return redirect('verify_code')
    else:
        form = UserCreationForm()
    return render(request, 'store/inscription.html', {'form': form})


def verify_code_view(request):
    user_id = request.session.get('verify_user_id')
    if not user_id:
        return redirect('inscription')
    
    user = User.objects.get(id=user_id)
    verification = EmailVerification.objects.get(user=user)

    if request.method == 'POST':
        entered_code = request.POST.get('code')
        
        if entered_code == verification.code:
            user.is_active = True
            user.save()
            
            verification.delete()
            del request.session['verify_user_id']
            
            messages.success(request, "Kont ou aktive avèk siksè! Ou ka konekte kounye a.")
            return redirect('connexion')
        else:
            messages.error(request, "Kòd la pa bon. Eseye ankò.")

    return render(request, 'store/verify_code.html')


def connexion_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accueil')
    else:
        form = AuthenticationForm()
    return render(request, 'store/connexion.html', {'form': form})


def deconnexion_user(request):
    logout(request)
    return redirect('accueil')


def apropos(request):
    return render(request, 'store/apropos.html')


def categories(request):
    categories_list = Categorie.objects.all()
    categorie_id = request.GET.get('categorie')
    
    if categorie_id:
        produits = Produit.objects.filter(categorie_id=categorie_id)
    else:
        produits = Produit.objects.all()

    context = {
        'categories': categories_list,
        'produits': produits,
        'selected_categorie': int(categorie_id) if categorie_id else None
    }
    return render(request, 'store/categories.html', context)


def recherche(request):
    query = request.GET.get('q', '').strip()
    produits = []
    
    if query:
        produits = Produit.objects.filter(
            Q(nom__icontains=query) | Q(description__icontains=query)
        )
        
    context = {
        'query': query,
        'produits': produits,
    }
    return render(request, 'store/recherche.html', context)


@login_required(login_url='connexion')
def mes_commandes(request):
    commandes = Commande.objects.filter(user=request.user).order_by('-date_commande')
    return render(request, 'store/mes_commandes.html', {'commandes': commandes})


def detail_produit(request, produit_id):
    produit = get_object_or_404(Produit, id=produit_id)
    return render(request, 'store/detail_produit.html', {'produit': produit})


@staff_member_required
def gestion_commandes(request):
    if request.method == 'POST':
        commande_id = request.POST.get('commande_id')
        nouveau_statut = request.POST.get('statut')
        if commande_id and nouveau_statut:
            commande = get_object_or_404(Commande, id=commande_id)
            commande.statut = nouveau_statut
            commande.save()
            return redirect('gestion_commandes')

    commandes = Commande.objects.all().order_by('-date_commande')
    return render(request, 'store/gestion_commandes.html', {'commandes': commandes})