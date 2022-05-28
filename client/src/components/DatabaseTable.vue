<template>
  <div class="container">
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Enter time</th>
          <th>Exit time</th>
          <th>Room</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in table" :key="index">
          <td>{{ row.enterTime }}</td>
          <td>{{ row.exitTime }}</td>
          <td>{{ row.uuid}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

export default {
  name: 'DatabaseTable',
  props: ['table'],
  data() {

  },
  methods: {

  },
};
</script>
