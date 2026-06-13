<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { logout, useCurrentUser } from '../services/auth'

const route = useRoute()
const router = useRouter()
const currentUser = useCurrentUser()

const shouldShowNav = computed(() => Boolean(route.meta.requiresAuth))
const currentUserLabel = computed(
  () => currentUser.value?.display_name ?? currentUser.value?.username ?? '已登录',
)

const handleLogout = () => {
  logout()
  router.replace('/')
}
</script>

<template>
  <header v-if="shouldShowNav" class="app-nav">
    <RouterLink class="nav-brand" to="/plan" aria-label="返回规划行程">
      <span>AI Travel Assistant</span>
    </RouterLink>

    <nav class="nav-links" aria-label="主导航">
      <RouterLink to="/plan">规划行程</RouterLink>
      <RouterLink to="/my-trips">我的行程</RouterLink>
    </nav>

    <div class="nav-account">
      <span>{{ currentUserLabel }}</span>
      <button type="button" @click="handleLogout">退出登录</button>
    </div>
  </header>
</template>

<style scoped>
.app-nav {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: minmax(180px, 1fr) auto minmax(180px, 1fr);
  gap: 18px;
  align-items: center;
  min-height: 68px;
  padding: 0 clamp(18px, 4vw, 56px);
  background: rgba(248, 251, 248, 0.92);
  border-bottom: 1px solid rgba(23, 107, 93, 0.12);
  box-shadow: 0 12px 34px rgba(31, 48, 39, 0.08);
  backdrop-filter: blur(16px);
}

.nav-brand {
  width: fit-content;
  color: var(--primary-dark);
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 0;
  text-decoration: none;
}

.nav-links {
  display: inline-flex;
  gap: 6px;
  align-items: center;
  justify-self: center;
  padding: 4px;
  background: rgba(23, 107, 93, 0.07);
  border: 1px solid rgba(23, 107, 93, 0.1);
  border-radius: 8px;
}

.nav-links a {
  display: inline-flex;
  min-height: 38px;
  align-items: center;
  padding: 0 16px;
  color: var(--primary-dark);
  border-radius: 6px;
  font-size: 14px;
  font-weight: 900;
  text-decoration: none;
}

.nav-links a.router-link-active {
  color: #ffffff;
  background: var(--primary);
  box-shadow: 0 10px 22px rgba(23, 107, 93, 0.18);
}

.nav-account {
  display: inline-flex;
  gap: 10px;
  align-items: center;
  justify-self: end;
}

.nav-account span {
  display: inline-flex;
  min-height: 38px;
  align-items: center;
  padding: 0 13px;
  color: var(--primary-dark);
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 900;
}

.nav-account button {
  min-height: 38px;
  padding: 0 14px;
  color: var(--primary-dark);
  background: transparent;
  border: 1px solid rgba(23, 107, 93, 0.22);
  border-radius: 6px;
  font-size: 13px;
  font-weight: 900;
}

@media (max-width: 760px) {
  .app-nav {
    grid-template-columns: 1fr;
    gap: 10px;
    justify-items: start;
    padding: 14px 16px;
  }

  .nav-links {
    justify-self: stretch;
  }

  .nav-links a {
    flex: 1;
    justify-content: center;
  }

  .nav-account {
    justify-self: stretch;
    justify-content: space-between;
  }
}
</style>
