import { createApp } from 'vue'
import axios from 'axios';

import store from './store/index.js';
import router from './router.js';

import App from './App.vue'

import BaseButton from './ui/BaseButton.vue';
import BaseDialog from './ui/BaseDialog.vue';
import BaseSpinner from './ui/BaseSpinner.vue';

const app = createApp(App);

app.component('base-button', BaseButton);
app.component('base-dialog', BaseDialog);
app.component('base-spinner', BaseSpinner);

app.use(router);
app.use(store);

app.mount('#app');

function getCSRFToken() {
  const cookieValue = document.cookie
    .split('; ')
    .find((cookie) => cookie.startsWith('csrftoken='))
    .split('=')[1];

  return cookieValue;
}

axios.defaults.headers.common['X-CSRFToken'] = getCSRFToken();