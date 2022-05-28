import { createRouter, createWebHistory } from 'vue-router';
import Pingitem from '../components/Ping.vue';
import DatabaseTable from '../components/DatabaseTable.vue';
import TracingApp from '../components/ContactTracingApp.vue';

const routes = [
  {
    path: '/ping',
    name: 'Ping',
    component: Pingitem,
  },
  {
    path: '/Database',
    name: 'Database',
    component: DatabaseTable,
  },
  {
    path: '/App',
    name: 'TracingApp',
    component: TracingApp,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
