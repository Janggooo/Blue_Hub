<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push(route.query.redirect || { name: 'dashboard' })
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not log in. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container auth-shell">
    <div class="hero-copy">
      <div class="tag">Welcome back</div>
      <h1>Log in to BlueHub</h1>
      <p>Pick up where you left off and continue exploring your organizations and events.</p>
    </div>

    <div class="card auth-card">
      <div v-if="error" class="error-banner">{{ error }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" required autocomplete="email" />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input id="password" v-model="password" type="password" required autocomplete="current-password" />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading" style="width:100%">
          {{ loading ? 'Logging in…' : 'Log in' }}
        </button>
      </form>
      <p class="switch">No account yet? <RouterLink to="/register">Sign up</RouterLink></p>
    </div>
  </div>
</template>

<style scoped>
.auth-shell {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 28px;
  align-items: center;
  max-width: 980px;
}
.hero-copy h1 {
  font-size: clamp(2rem, 3.2vw, 2.8rem);
  margin: 10px 0 12px;
}
.hero-copy p {
  color: var(--ink-soft);
  font-size: 1rem;
  line-height: 1.6;
  max-width: 520px;
}
.auth-card { width: 100%; }
.switch { text-align: center; margin-top: 16px; font-size: 0.9rem; color: var(--ink-soft); }
.switch a { color: var(--cobalt); font-weight: 600; }
@media (max-width: 820px) {
  .auth-shell { grid-template-columns: 1fr; }
  .hero-copy { text-align: center; }
}
</style>
