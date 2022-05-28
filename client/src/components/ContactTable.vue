<template>
  <div class="container">
    <h2>Close Contacts</h2>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Device ID</th>
          <th>Rooms</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in table" :key="index">
          <td>{{ row.deviceID }}</td>
          <td>{{ row.uuid.toString().replace('[', '').replace(']', '') }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

export default {
  name: 'ContactTable',
  props: ['table'],
  data() {

  },
  methods: {

  },
};
</script>
