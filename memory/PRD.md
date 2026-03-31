# Econnect VTC - Product Requirements Document

## Original Problem Statement
Améliorer le site internet VTC econnect-vtc.com avec:
- Design luxueux noir et doré
- Système de connexion clients et administrateur
- Partie admin pour envoyer les courses aux chauffeurs
- Toutes les options: Google Maps, notifications email

## User Personas
- **Clients**: Réservation de courses VTC
- **Chauffeurs**: Réception et gestion des courses assignées
- **Administrateur**: Gestion globale (chauffeurs, courses, clients)

## Core Requirements
- Design luxueux noir (#0A0A0A) et doré (#D4AF37)
- Authentification JWT (email/password)
- 3 rôles utilisateurs (client, driver, admin)
- Dashboard admin avec statistiques
- Assignation des courses aux chauffeurs
- Notifications dashboard + email (SendGrid)

## What's Been Implemented (Jan 2026)

### Backend (FastAPI + MongoDB)
- **Auth System**: JWT tokens, bcrypt hashing, role-based access
- **User Management**: Registration, login, logout, session management
- **Booking System**: CRUD operations, status workflow (pending → assigned → in_progress → completed)
- **Admin APIs**: Stats, assign bookings, manage drivers, view clients
- **Driver APIs**: View assigned bookings, update status, availability toggle
- **Email Service**: SendGrid integration for driver notifications

### Frontend (React + Tailwind)
- **Landing Page**: Hero, Services (bento grid), Booking form, Testimonials, Footer, WhatsApp button
- **Auth Pages**: Login, Register with validation
- **Client Dashboard**: Stats, booking history, new booking form
- **Driver Dashboard**: Assigned courses, status updates, availability toggle
- **Admin Dashboard**: 
  - Stats overview (total bookings, pending, drivers, clients)
  - Bookings management with driver assignment modal
  - Drivers management (CRUD)
  - Clients list

### Tech Stack
- Backend: FastAPI, Motor (async MongoDB), PyJWT, bcrypt, SendGrid
- Frontend: React 19, Tailwind CSS, Framer Motion, Phosphor Icons
- Database: MongoDB
- Auth: JWT with httpOnly cookies

## Test Credentials
- **Admin**: admin@econnect-vtc.com / admin123

## Prioritized Backlog

### P0 (Critique) - DONE ✅
- [x] Design noir et doré
- [x] Système d'authentification
- [x] Dashboards client/driver/admin
- [x] Assignation des courses

### P1 (Important)
- [ ] Intégration Google Maps API (clé requise)
- [ ] Notifications email SendGrid (clé requise)
- [ ] Numéro WhatsApp réel
- [ ] Coordonnées contact réelles

### P2 (Nice to have)
- [ ] Google OAuth login
- [ ] Calcul de tarif automatique
- [ ] Historique des courses complet
- [ ] Notifications push
- [ ] Mode sombre/clair

## API Endpoints

### Auth
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/logout
- GET /api/auth/me

### Admin
- GET /api/admin/stats
- GET /api/admin/bookings
- PUT /api/admin/bookings/{id}/assign
- GET/POST/DELETE /api/admin/drivers
- GET /api/admin/clients

### Driver
- GET /api/driver/bookings
- PUT /api/driver/bookings/{id}/status
- PUT /api/driver/availability

### Client
- POST /api/bookings
- GET /api/bookings/my
