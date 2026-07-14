<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const users = ref([])
const orgs = ref([])
const loading = ref(true)
const error = ref('')
const form = ref({ first_name: '', last_name: '', email: '', password: '', role: 'student', organization_id: '' })

async function loadUsers() {
  loading.value = true
  error.value = ''
  try {
    const res = await client.get('/users')
    users.value = res.data
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not load users.'
  } finally {
    loading.value = false
  }
}

async function loadOrgs() {
  try {
    const res = await client.get('/organizations')
    orgs.value = res.data
  } catch (e) {
    // ignore
  }
}

async function createUser() {
  error.value = ''
  try {
    await client.post('/users', form.value)
    form.value = { first_name: '', last_name: '', email: '', password: '', role: 'student', organization_id: '' }
    await loadUsers()
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not create user.'
  }
}

async function deleteUser(userId) {
  if (!confirm('Delete this user?')) return
  try {
    await client.delete(`/users/${userId}`)
    await loadUsers()
  } catch (e) {
    error.value = e.response?.data?.error || 'Could not delete user.'
  }
}

onMounted(() => {
  loadUsers()
  loadOrgs()
})
</script>

<template>
  <div class="container">
    <h1>User management</h1>
    <div v-if="error" class="error-banner">{{ error }}</div>
    <div class="card">
      <h2>Create user</h2>
      <form @submit.prevent="createUser">
        <div class="field"><label>First name</label><input v-model="form.first_name" required /></div>
        <div class="field"><label>Last name</label><input v-model="form.last_name" required /></div>
        <div class="field"><label>Email</label><input v-model="form.email" type="email" required /></div>
        <div class="field"><label>Password</label><input v-model="form.password" type="password" required /></div>
        <div class="field"><label>Role</label>
          <select v-model="form.role">
            <option value="student">Student</option>
            <option value="officer">Officer</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <div class="field" v-if="form.role === 'officer'">
          <label>Organization</label>
          <select v-model="form.organization_id" required>
            <option value="" disabled>Select organization</option>
            <option v-for="org in orgs" :key="org.organization_id" :value="org.organization_id">{{ org.organization_name }}</option>
          </select>
        </div>
        <button class="btn btn-primary" type="submit">Create user</button>
      </form>
    </div>

    <div class="card" style="margin-top:24px;">
      <h2>All users</h2>
      <div v-if="loading" class="empty-state">Loading users…</div>
      <table v-else class="user-table">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Role</th><th>Org ID</th><th>Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.user_id">
            <td>{{ user.first_name }} {{ user.last_name }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>{{ user.organization_id || '—' }}</td>
            <td><button class="btn btn-danger" @click="deleteUser(user.user_id)">Delete</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.user-table { width: 100%; border-collapse: collapse; }
.user-table th, .user-table td { padding: 12px 10px; text-align: left; border-bottom: 1px solid var(--line); }
.user-table th { color: var(--ink-soft); }
.field { margin-bottom: 14px; }
</style>