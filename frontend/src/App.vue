<script setup>
import { useAuthStore } from './store/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push({ name: 'events' })
}
</script>

<template>
  <header class="nav">
    <div class="container nav-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">BH</span>
        <span>BlueHub</span>
      </RouterLink>

      <nav class="nav-links">
        <RouterLink to="/" active-class="active">Events</RouterLink>
        <RouterLink to="/organizations" active-class="active">Organizations</RouterLink>
        <RouterLink v-if="auth.role === 'admin'" to="/users" active-class="active">Users</RouterLink>
        <RouterLink v-if="auth.isAuthenticated" to="/dashboard" active-class="active">Dashboard</RouterLink>
      </nav>

      <div class="nav-auth">
        <template v-if="auth.isAuthenticated">
          <span class="hello">Hi, {{ auth.user.first_name }}</span>
          <button class="btn btn-ghost" @click="handleLogout">Log out</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="btn btn-ghost">Log in</RouterLink>
          <RouterLink to="/register" class="btn btn-primary">Sign up</RouterLink>
        </template>
      </div>
    </div>
  </header>

  <main class="main">
    <RouterView />
  </main>

  <footer class="footer">
    <div class="container">BlueHub — a BlueByte project for the ADNU community.</div>
  </footer>
</template>

<style scoped>
.nav {
  background: linear-gradient(90deg, var(--ink) 0%, #1b2d4d 100%);
  color: #fff;
  border-bottom: 3px solid var(--gold);
  box-shadow: 0 8px 24px rgba(18, 35, 61, 0.16);
}
.nav-inner {
  display: flex;
  align-items: center;
  gap: 28px;
  padding-top: 14px;
  padding-bottom: 14px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1.15rem;
  color: #fff;
}
.brand-mark {
  background: var(--cobalt);
  color: #fff;
  font-size: 0.8rem;
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.nav-links {
  display: flex;
  gap: 20px;
  flex: 1;
}
.nav-links a {
  color: #C7D0E3;
  font-weight: 500;
  padding: 6px 0;
  border-bottom: 2px solid transparent;
}
.nav-links a:hover { color: #fff; }
.nav-links a.active { color: #fff; border-bottom-color: var(--gold); }

.nav-auth {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-auth .btn-ghost { color: #fff; border-color: #445070; }
.hello { color: #C7D0E3; font-size: 0.9rem; }

.main {
  flex: 1;
  padding: 42px 0 64px;
}

.footer {
  border-top: 1px solid var(--line);
  padding: 20px 0;
  color: var(--ink-soft);
  font-size: 0.85rem;
}
</style>
