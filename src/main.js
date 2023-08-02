import { createApp } from 'vue'

import store from './store/index.js';
import router from './router.js';

import App from './App.vue'

import BaseButton from './ui/BaseButton.vue';
import BaseDialog from './ui/BaseDialog.vue';

const app = createApp(App);

app.component('base-button', BaseButton);
app.component('base-dialog', BaseDialog);

app.use(router);
app.use(store);

app.mount('#app');
