<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { login } from '../services/auth'

const router = useRouter()
const route = useRoute()

const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)
const errorMessage = ref('')
const defaultAccountHint = computed(() => '默认账号 demo / travel123')

const resolveRedirect = () => {
  const redirect = route.query.redirect
  if (typeof redirect === 'string' && redirect.startsWith('/') && redirect !== '/') {
    return redirect
  }

  return '/plan'
}

const handleSubmit = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    await login({
      username: form.username.trim(),
      password: form.password,
    })

    await router.replace(resolveRedirect())
  } catch {
    errorMessage.value = '账号或密码错误，请重新输入。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-page">
    <section class="auth-card" aria-labelledby="login-title">
      <div class="visual-panel" aria-hidden="true">
        <div class="visual-image"></div>
      </div>

      <section class="login-panel">
        <a class="brand-logo" href="/" aria-label="智能旅游助手首页">
          <span class="brand-name">AI Travel Assistant</span>
        </a>

        <div class="panel-heading">
          <p class="eyebrow">Sign in</p>
          <h1 id="login-title">登录账号</h1>
          <span>{{ defaultAccountHint }}</span>
        </div>

        <form class="login-form" @submit.prevent="handleSubmit">
          <label class="field">
            <span>账号</span>
            <input
              v-model.trim="form.username"
              type="text"
              autocomplete="username"
              placeholder="请输入账号"
              required
            />
          </label>

          <label class="field">
            <span>密码</span>
            <input
              v-model="form.password"
              type="password"
              autocomplete="current-password"
              placeholder="请输入密码"
              required
            />
          </label>

          <button class="submit-button" type="submit" :disabled="loading">
            <span>{{ loading ? '登录中...' : '登录并填写出发计划' }}</span>
          </button>

          <p v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </p>
        </form>
      </section>
    </section>

    <footer class="site-footer">
      <span>© 2026 AI Travel Assistant. All rights reserved.</span>
    </footer>
  </main>
</template>

<style scoped>
.login-page {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 100vh;
  padding: 48px clamp(18px, 4vw, 56px);
  overflow: hidden;
  background:
    linear-gradient(135deg, rgba(170, 185, 178, 0.56), rgba(213, 221, 216, 0.72)),
    #c8d2cc;
}

.login-page::before {
  position: absolute;
  inset: -18% -8%;
  content: "";
  pointer-events: none;
  background:
    radial-gradient(circle at 16% 82%, rgba(23, 107, 93, 0.09) 0 12%, transparent 12.4%),
    radial-gradient(circle at 78% 2%, rgba(23, 107, 93, 0.08) 0 18%, transparent 18.4%),
    linear-gradient(100deg, transparent 0 58%, rgba(255, 255, 255, 0.34) 58.3% 66%, transparent 66.3%);
}

.auth-card,
.login-panel,
.site-footer {
  position: relative;
  z-index: 1;
}

.auth-card {
  display: grid;
  grid-template-columns: minmax(320px, 0.92fr) minmax(420px, 1.08fr);
  width: min(100%, 980px);
  min-height: 560px;
  overflow: hidden;
  background: transparent;
  border: 0;
  border-radius: 8px;
  box-shadow: 0 34px 86px rgba(42, 63, 54, 0.24);
  backdrop-filter: blur(18px);
}

.visual-panel {
  min-height: 560px;
  background: transparent;
}

.visual-image {
  width: 100%;
  height: 100%;
  min-height: inherit;
  background:
    linear-gradient(180deg, rgba(10, 62, 45, 0.08), rgba(10, 62, 45, 0.24)),
    url("https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1000&q=86");
  background-position: center;
  background-size: cover;
}

.brand-logo {
  display: inline-flex;
  width: fit-content;
  align-items: center;
  color: var(--primary-dark);
  text-decoration: none;
}

.brand-name {
  color: #176b5d;
  font-size: 20px;
  font-weight: 900;
  letter-spacing: 0;
}

.login-panel {
  display: grid;
  align-content: center;
  width: 100%;
  padding: clamp(36px, 5vw, 64px);
  transform: none;
  background: rgba(240, 245, 241, 0.94);
  border-left: 1px solid rgba(23, 107, 93, 0.08);
  box-shadow: none;
  backdrop-filter: blur(16px);
}

.panel-heading {
  display: grid;
  gap: 10px;
  margin-top: 42px;
  margin-bottom: 30px;
}

.eyebrow {
  display: flex;
  width: fit-content;
  min-height: 32px;
  align-items: center;
  padding: 0;
  margin: 0;
  color: #66736a;
  background: transparent;
  border: 0;
  border-radius: 0;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.panel-heading h1 {
  margin: 0;
  color: var(--text);
  font-size: clamp(30px, 3.5vw, 40px);
  line-height: 1.16;
  font-weight: 900;
}

.panel-heading span {
  color: var(--muted);
  font-size: 14px;
  font-weight: 700;
}

.login-form {
  display: grid;
  gap: 18px;
}

.field {
  display: grid;
  gap: 9px;
}

.field span {
  color: #3b463f;
  font-size: 14px;
  font-weight: 800;
}

.field input {
  width: 100%;
  min-height: 58px;
  padding: 0 18px;
  color: var(--text);
  background: #ffffff;
  border: 1px solid #d8e2d8;
  border-radius: 4px;
  outline: none;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 10px 24px rgba(31, 48, 39, 0.04);
}

.field input:focus {
  border-color: rgba(23, 107, 93, 0.74);
  box-shadow: 0 0 0 3px rgba(23, 107, 93, 0.12);
}

.submit-button {
  display: inline-flex;
  min-height: 60px;
  align-items: center;
  justify-content: center;
  margin-top: 6px;
  color: #ffffff;
  background: #176b5d;
  border: 1px solid rgba(23, 107, 93, 0.12);
  border-radius: 4px;
  box-shadow: 0 16px 34px rgba(23, 107, 93, 0.2);
  font-size: 16px;
  font-weight: 900;
  cursor: pointer;
  transition:
    background 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  background: #0f4b42;
  box-shadow: 0 20px 38px rgba(23, 107, 93, 0.26);
  transform: translateY(-1px);
}

.submit-button:disabled {
  opacity: 0.7;
  cursor: wait;
}

.error-message {
  margin: 0;
  color: #b63a2b;
  font-size: 14px;
  font-weight: 800;
}

.site-footer {
  position: absolute;
  right: 50%;
  bottom: 22px;
  transform: translateX(50%);
  color: rgba(80, 94, 104, 0.66);
  font-size: 14px;
}

@media (max-width: 980px) {
  .login-page {
    padding: 28px 16px 54px;
    overflow: visible;
  }

  .auth-card {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .visual-panel {
    min-height: 240px;
  }

  .visual-image {
    min-height: 240px;
  }

  .login-panel {
    border-left: 0;
  }

  .site-footer {
    right: 50%;
    bottom: 22px;
    color: rgba(80, 94, 104, 0.66);
  }
}

@media (max-width: 560px) {
  .login-page {
    padding: 18px 12px 54px;
  }

  .login-panel {
    padding: 20px;
  }

  .visual-panel,
  .visual-image {
    min-height: 190px;
  }

  .panel-heading {
    margin-top: 24px;
  }
}
</style>
