<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const props = defineProps({ id: { type: String, required: true } })
const router = useRouter()

const form = ref({ organization_name: '', description: '', category: '', contact_email: '', logo_url: '' })
const error = ref('')
const loading = ref(false)

async function loadOrg() {
  const { data } = await client.get(`/organizations/${props.id}`)
  form.value = {
    organization_name: data.organization_name,
    description: data.description,
    category: data.category,
    contact_email: data.contact_email,
    logo_url: data.logo_url
  }
}

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    await client.put(`/organizations/${props.id}`, form.value)
    router.push({ name: 'org-profile', params: { id: props.id } })
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not save changes.'
  } finally {
    loading.value = false
  }
}

onMounted(loadOrg)
</script>

<template>
  <div class="container narrow">
    <h1>Edit organization profile</h1>

    <div class="card">
      <div v-if="error" class="error-banner">{{ error }}</div>
      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label for="organization_name">Organization name</label>
          <input id="organization_name" v-model="form.organization_name" required />
        </div>
        <div class="field">
          <label for="description">Description</label>
          <textarea id="description" v-model="form.description" rows="5"></textarea>
        </div>
        <div class="field">
          <label for="category">Category</label>
          <input id="category" v-model="form.category" placeholder="e.g. Technology, Sports, Cultural" />
        </div>
        <div class="field">
          <label for="contact_email">Contact email</label>
          <input id="contact_email" v-model="form.contact_email" type="email" />
        </div>
        <div class="field">
          <label for="logo_url">Logo URL (optional)</label>
          <input id="logo_url" v-model="form.logo_url" placeholder="https://…" />
        </div>

        <button class="btn btn-primary" type="submit" :disabled="loading" style="width:100%">
          {{ loading ? 'Saving…' : 'Save changes' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.narrow { max-width: 560px; }
h1 { margin-bottom: 20px; }
</style>
