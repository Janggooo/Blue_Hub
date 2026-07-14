<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const props = defineProps({ id: { type: String, default: null } })
const router = useRouter()
const auth = useAuthStore()

const isEdit = computed(() => !!props.id)
const isAdmin = computed(() => auth.role === 'admin')
const form = ref({
  organization_id: auth.user?.organization_id || '',
  title: '',
  description: '',
  venue: '',
  event_date: '',
  category: '',
  image_url: ''
})
const categories = ref([])
const organizations = ref([])
const error = ref('')
const loading = ref(false)

async function loadCategories() {
  try {
    const { data } = await client.get('/categories')
    categories.value = data
  } catch (e) { /* non-critical */ }
}

async function loadOrganizations() {
  if (!isAdmin.value) return
  try {
    const { data } = await client.get('/organizations')
    organizations.value = data
  } catch (e) { /* non-critical */ }
}

async function loadEvent() {
  const { data } = await client.get(`/events/${props.id}`)
  form.value = {
    organization_id: data.organization_id,
    title: data.title,
    description: data.description,
    venue: data.venue,
    event_date: data.event_date ? data.event_date.substring(0, 10) : '',
    category: data.category,
    image_url: data.image_url
  }
}

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    if (isEdit.value) {
      await client.put(`/events/${props.id}`, form.value)
      router.push({ name: 'event-detail', params: { id: props.id } })
    } else {
      const { data } = await client.post('/events', form.value)
      router.push({ name: 'event-detail', params: { id: data.event_id } })
    }
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not save this event.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadOrganizations()
  if (isEdit.value) loadEvent()
})
</script>

<template>
  <div class="container narrow">
    <h1>{{ isEdit ? 'Edit event' : 'Create an event' }}</h1>

    <div class="card">
      <div v-if="error" class="error-banner">{{ error }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="field" v-if="isAdmin">
          <label for="organization_id">Organization</label>
          <select id="organization_id" v-model="form.organization_id" required>
            <option value="" disabled>Select organization</option>
            <option v-for="org in organizations" :key="org.organization_id" :value="org.organization_id">
              {{ org.organization_name }}
            </option>
          </select>
        </div>

        <div class="field">
          <label for="title">Title</label>
          <input id="title" v-model="form.title" required />
        </div>
        <div class="field">
          <label for="description">Description</label>
          <textarea id="description" v-model="form.description" rows="4"></textarea>
        </div>
        <div class="row">
          <div class="field">
            <label for="event_date">Date</label>
            <input id="event_date" v-model="form.event_date" type="date" required />
          </div>
          <div class="field">
            <label for="category">Category</label>
            <select id="category" v-model="form.category">
              <option value="">Select category</option>
              <option v-for="c in categories" :key="c.category_id" :value="c.category_name">{{ c.category_name }}</option>
            </select>
          </div>
        </div>
        <div class="field">
          <label for="venue">Venue</label>
          <input id="venue" v-model="form.venue" />
        </div>
        <div class="field">
          <label for="image_url">Image URL (optional)</label>
          <input id="image_url" v-model="form.image_url" placeholder="https://…" />
        </div>

        <button class="btn btn-primary" type="submit" :disabled="loading" style="width:100%">
          {{ loading ? 'Saving…' : isEdit ? 'Save changes' : 'Create event' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 560px; }
h1 { margin-bottom: 20px; }
.row { display: flex; gap: 12px; }
.row .field { flex: 1; }
</style>
