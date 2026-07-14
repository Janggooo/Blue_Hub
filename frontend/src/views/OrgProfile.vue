<script setup>
import { ref, onMounted, computed } from 'vue'
import client from '../api/client'
import EventCard from '../components/EventCard.vue'
import { useAuthStore } from '../store/auth'

const props = defineProps({ id: { type: String, required: true } })
const auth = useAuthStore()

const org = ref(null)
const loading = ref(true)
const error = ref('')

const canManage = computed(() => {
  if (!org.value || !auth.isAuthenticated) return false
  return auth.role === 'admin' || (auth.role === 'officer' && auth.user.organization_id === org.value.organization_id)
})

async function fetchOrg() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get(`/organizations/${props.id}`)
    org.value = data
  } catch (e) {
    error.value = 'This organization could not be found.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchOrg)
</script>

<template>
  <div class="container narrow">
    <RouterLink to="/organizations" class="back">← Back to organizations</RouterLink>

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-else-if="loading" class="empty-state">Loading…</div>

    <template v-else-if="org">
      <div class="card">
        <span v-if="org.category" class="tag">{{ org.category }}</span>
        <h1>{{ org.organization_name }}</h1>
        <p v-if="org.contact_email" class="meta">✉️ {{ org.contact_email }}</p>
        <p class="description">{{ org.description }}</p>

        <div v-if="canManage" class="actions">
          <RouterLink :to="`/organizations/${org.organization_id}/edit`" class="btn btn-ghost">Edit profile</RouterLink>
          <RouterLink to="/events/new" class="btn btn-primary">Post an event</RouterLink>
        </div>
      </div>

      <h2 class="section-title">Upcoming events</h2>
      <div v-if="org.upcoming_events.length === 0" class="empty-state">No upcoming events yet.</div>
      <div v-else class="grid">
        <EventCard v-for="e in org.upcoming_events" :key="e.event_id" :event="{ ...e, organization_name: org.organization_name }" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.narrow { max-width: 680px; }
.back { display: inline-block; margin-bottom: 16px; color: var(--ink-soft); font-size: 0.9rem; }
h1 { margin: 10px 0 8px; font-size: 1.6rem; }
.meta { color: var(--ink-soft); font-size: 0.92rem; margin: 4px 0; }
.description { margin-top: 18px; line-height: 1.6; white-space: pre-wrap; }
.actions { display: flex; gap: 10px; margin-top: 26px; }
.section-title { margin: 32px 0 16px; font-size: 1.2rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
</style>
