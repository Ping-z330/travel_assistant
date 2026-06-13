import {createRouter, createWebHistory} from 'vue-router'
import { ensureAuthReady, isAuthenticated } from '../services/auth'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import MyTripsView from '../views/MyTripsView.vue'
import ResultView from '../views/ResultView.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'login',
            component: LoginView,
            meta: {
                guestOnly: true,
            },
        },
        {
            path: '/login',
            redirect: '/',
        },
        {
            path: '/plan',
            name: 'plan',
            component: HomeView,
            meta: {
                requiresAuth: true,
            },
        },
        {
            path: '/result',
            name: 'result',
            component: ResultView,
            meta: {
                requiresAuth: true,
            },
        },
        {
            path: '/my-trips',
            name: 'my-trips',
            component: MyTripsView,
            meta: {
                requiresAuth: true,
            },
        },
    ],
})

router.beforeEach(async (to) => {
    await ensureAuthReady()

    if (to.meta.guestOnly && isAuthenticated()) {
        return { path: '/plan' }
    }

    if (to.meta.requiresAuth && !isAuthenticated()) {
        return {
            path: '/',
            query: {
                redirect: to.fullPath,
            },
        }
    }

    return true
})

export default router
