,<template>
  <div class="container">
    <button type="button" class="btn btn-primary">{{ msg }}</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PingItem',
  data() {
    return {
      msg: 'Not connected to backend!',
    };
  },
  methods: {
    getMessage() {
      const path = 'http://159.196.72.33:5000/ping';
      axios.get(path)
        .then((response) => {
          this.msg = response.data;
        })
        .catch((error) => {
          // eslint-disable-next-line
          console.error(error);
        });
    },
  },
  created() {
    this.getMessage();
  },
};
</script>
