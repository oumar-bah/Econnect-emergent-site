# Econnect VTC - Product Requirements Document

## Original Problem Statement
Améliorer le site internet VTC econnect-vtc.com avec un design luxueux noir et doré.

## User Personas
- **Professionnels**: Cadres, dirigeants nécessitant des déplacements business
- **Voyageurs fréquents**: Personnes utilisant les transferts aéroports/gares
- **Organisateurs d'événements**: Gestion de transports pour groupes
- **Particuliers**: Services de chauffeur privé pour occasions spéciales

## Core Requirements
- Design luxueux noir (#0A0A0A) et doré (#D4AF37)
- Landing page responsive (mobile, tablette, desktop)
- Formulaire de réservation intuitif
- Carte interactive avec Paris
- Sections: Hero, Services, Réservation, Pourquoi nous, Témoignages, Footer
- Bouton WhatsApp flottant pour contact direct

## What's Been Implemented (Jan 2026)

### Frontend Components
- **Navbar**: Navigation glassmorphique avec liens et CTA
- **Hero**: Section plein écran avec image de voiture de luxe
- **Services**: Grille Bento avec 4 services (Trajets Ponctuels, Mise à Disposition, Transferts Aéroports, Affaires)
- **BookingSection**: Formulaire complet (date, heure, adresses, type de transfert)
- **InteractiveMap**: Carte Leaflet avec tiles CartoDB Dark
- **WhyChooseUs**: 4 avantages (Ponctualité, Sécurité, Excellence, Confort)
- **Testimonials**: 3 témoignages clients
- **Footer**: Contact, réseaux sociaux, liens de navigation
- **WhatsAppButton**: Bouton flottant avec animation

### Design Features
- Smooth scrolling avec Lenis
- Animations Framer Motion
- Icons Phosphor React
- Typographie: Cormorant Garamond (titres) + Outfit (corps)
- Glassmorphisme et effets de glow dorés

## Prioritized Backlog

### P0 (Critique)
- ✅ Complété

### P1 (Important)
- [ ] Intégration numéro WhatsApp réel
- [ ] Ajout vraies coordonnées contact
- [ ] SEO meta tags

### P2 (Nice to have)
- [ ] Système de devis automatique avec calcul de distance
- [ ] Paiement en ligne Stripe
- [ ] Espace client avec historique
- [ ] Multi-langues (FR/EN)

## Tech Stack
- React 19 avec Tailwind CSS
- Framer Motion pour animations
- React-Leaflet pour la carte
- Phosphor Icons
- Lenis pour smooth scroll
- Shadcn/UI components

## Next Tasks
1. Mettre à jour le numéro WhatsApp réel
2. Ajouter les vraies coordonnées de contact
3. Configurer les méta tags SEO
