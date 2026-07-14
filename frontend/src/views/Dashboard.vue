<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client'
import EventCard from '../components/EventCard.vue'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const data = ref(null)
const loading = ref(true)
const error = ref('')

async function fetchDashboard() {
  loading.value = true
  error.value = ''
  try {
    const res = await client.get('/dashboard')
    data.value = res.data
  } catch (e) {
    error.value = 'Could not load your dashboard.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchDashboard)
</script>

<template>
  <div class="container">
    <h1>Dashboard</h1>

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-else-if="loading" class="empty-state">Loading…</div>

    <template v-else-if="data">
      <div class="card profile-card">
        <p class="label">Signed in as</p>
        <h2>{{ data.user.first_name }} {{ data.user.last_name }}</h2>
        <p class="meta">{{ data.user.email }} · <span class="tag">{{ data.user.role }}</span></p>
      </div>

      <template v-if="data.organization">
        <div class="section-head">
          <h2>Managing: {{ data.organization.organization_name }}</h2>
          <div class="head-actions">
            <RouterLink :to="`/organizations/${data.organization.organization_id}/edit`" class="btn btn-ghost">Edit org profile</RouterLink>
            <RouterLink to="/events/new" class="btn btn-primary">+ New event</RouterLink>
          </div>
        </div>

        <div v-if="data.managed_events.length === 0" class="empty-state">
          You haven't posted any events yet.
        </div>
        <div v-else class="grid">
          <EventCard
            v-for="e in data.managed_events"
            :key="e.event_id"
            :event="{ ...e, organization_name: data.organization.organization_name }"
          />
        </div>
      </template>

      <template v-else-if="data.user.role === 'admin'">
        <div class="section-head">
          <h2>Admin management</h2>
          <div class="head-actions">
            <RouterLink to="/users" class="btn btn-primary">Manage users</RouterLink>
            <RouterLink to="/organizations" class="btn btn-secondary">Browse organizations</RouterLink>
            <RouterLink to="/" class="btn btn-ghost">Browse events</RouterLink>
          </div>
        </div>
        <div class="empty-state">
          As an administrator, you can edit any organization or event from its page.
        </div>
      </template>

      <div v-else>
        <div class="empty-state">
          You're browsing as a student. Explore the
          <RouterLink to="/">event directory</RouterLink> or
          <RouterLink to="/organizations">organizations</RouterLink> to get involved.
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
h1 { margin-bottom: 20px; }
.profile-card { margin-bottom: 32px; }
.label { font-size: 0.8rem; color: var(--ink-soft); margin: 0 0 4px; text-transform: uppercase; letter-spacing: 0.04em; }
.meta { color: var(--ink-soft); margin-top: 8px; display: flex; align-items: center; gap: 8px; }
.section-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 18px; }
.head-actions { display: flex; gap: 10px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
</style>
