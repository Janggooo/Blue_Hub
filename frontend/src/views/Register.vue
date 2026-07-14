<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const form = ref({ first_name: '', last_name: '', email: '', password: '' })
const error = ref('')
const success = ref('')
const loading = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function handleSubmit() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    await auth.register(form.value)
    success.value = 'Account created successfully. You are now signed in.'
    setTimeout(() => router.push({ name: 'dashboard' }), 600)
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not create your account. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="container auth-shell">
    <div class="hero-copy">
      <div class="tag">New account</div>
      <h1>Create your BlueHub account</h1>
      <p>Join the community, discover organizations, and keep up with events tailored to your campus life.</p>
    </div>

    <div class="card auth-card">
      <div v-if="error" class="error-banner">{{ error }}</div>
      <div v-if="success" class="success-banner">{{ success }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="row">
          <div class="field">
            <label for="first_name">First name</label>
            <input id="first_name" v-model="form.first_name" required />
          </div>
          <div class="field">
            <label for="last_name">Last name</label>
            <input id="last_name" v-model="form.last_name" required />
          </div>
        </div>
        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" required autocomplete="email" />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input id="password" v-model="form.password" type="password" required minlength="8" autocomplete="new-password" />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading" style="width:100%">
          {{ loading ? 'Creating account…' : 'Sign up' }}
        </button>
      </form>
      <p class="hint">Officer or admin access is granted after signup by an administrator.</p>
      <p class="switch">Already have an account? <RouterLink to="/login">Log in</RouterLink></p>
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
.hero-copy {
  padding: 12px 0;
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
.row { display: flex; gap: 12px; }
.row .field { flex: 1; }
.hint { font-size: 0.8rem; color: var(--ink-soft); margin-top: 14px; }
.switch { text-align: center; margin-top: 10px; font-size: 0.9rem; color: var(--ink-soft); }
.switch a { color: var(--cobalt); font-weight: 600; }
@media (max-width: 820px) {
  .auth-shell { grid-template-columns: 1fr; }
  .hero-copy { text-align: center; }
}
</style>
