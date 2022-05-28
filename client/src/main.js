import { createApp } from 'vue';
import { BootstrapVue3 } from 'bootstrap-vue-3';
// import DatePicker from '@vuepic/vue-datepicker';
import App from './App.vue';
import router from './router';

import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue-3/dist/bootstrap-vue-3.css';
import '@vuepic/vue-datepicker/dist/main.css';

// createApp(App).use(router).mount('#app');
const app = createApp(App);
app.use(router);
app.use(BootstrapVue3);
// app.component('DatePicker', DatePicker);
app.mount('#app');
