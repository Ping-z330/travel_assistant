import {createRouter, createWebHistory} from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MyTripsView from '../views/MyTripsView.vue'
import ResultView from '../views/ResultView.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            name: 'home',
            component: HomeView,
        },
        {
            path: '/result',
            name: 'result',
            component: ResultView,
        },
        {
            path: '/my-trips',
            name: 'my-trips',
            component: MyTripsView,
        },
    ],
})

export default router
