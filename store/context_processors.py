def panier_context(request):
    panier = request.session.get('panier', {})
    
    # Kalkile total tout kantite ki nan panye session an
    nombre_articles_panier = sum(panier.values())
    
    return {
        'nombre_articles_panier': nombre_articles_panier
    }