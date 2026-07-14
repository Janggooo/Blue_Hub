<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const props = defineProps({ id: { type: String, required: true } })
const router = useRouter()
const auth = useAuthStore()

const event = ref(null)
const loading = ref(true)
const error = ref('')

const canManage = computed(() => {
  if (!event.value || !auth.isAuthenticated) return false
  return auth.role === 'admin' || (auth.role === 'officer' && auth.user.organization_id === event.value.organization_id)
})

function formatDate(d) {
  if (!d) return ''
  return new Date(d).toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
}

async function fetchEvent() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await client.get(`/events/${props.id}`)
    event.value = data
  } catch (e) {
    error.value = 'This event could not be found.'
  } finally {
    loading.value = false
  }
}

async function handleDelete() {
  if (!confirm('Delete this event? This cannot be undone.')) return
  try {
    await client.delete(`/events/${props.id}`)
    router.push({ name: 'events' })
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not delete this event.'
  }
}

onMounted(fetchEvent)
</script>

<template>
  <div class="container narrow">
    <RouterLink to="/" class="back">← Back to events</RouterLink>

    <div v-if="error" class="error-banner">{{ error }}</div>
    <div v-else-if="loading" class="empty-state">Loading…</div>

    <div v-else-if="event" class="card">
      <span v-if="event.category" class="tag">{{ event.category }}</span>
      <h1>{{ event.title }}</h1>
      <p class="meta">
        <RouterLink :to="`/organizations/${event.organization_id}`">{{ event.organization_name }}</RouterLink>
        · {{ formatDate(event.event_date) }}
      </p>
      <p v-if="event.venue" class="meta">📍 {{ event.venue }}</p>

      <p class="description">{{ event.description }}</p>

      <div v-if="canManage" class="actions">
        <RouterLink :to="`/events/${event.event_id}/edit`" class="btn btn-ghost">Edit event</RouterLink>
        <button class="btn btn-danger" @click="handleDelete">Delete event</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 680px; }
.back { display: inline-block; margin-bottom: 16px; color: var(--ink-soft); font-size: 0.9rem; }
h1 { margin: 10px 0 8px; font-size: 1.6rem; }
.meta { color: var(--ink-soft); font-size: 0.92rem; margin: 4px 0; }
.meta a { color: var(--cobalt); font-weight: 600; }
.description { margin-top: 18px; line-height: 1.6; white-space: pre-wrap; }
.actions { display: flex; gap: 10px; margin-top: 26px; }
</style>
