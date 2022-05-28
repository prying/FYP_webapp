<template>
  <div class="container">
    <table class="table table-striped">
      <thead>
        <tr>
          <th>time</th>
          <th>packet</th>
          <th>uuid</th>
          <th>rssi</th>
          <th>filtered rssi</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in table" :key="index">
          <td>{{ row.dateTime }}</td>
          <td>{{ row.pkGroup }}</td>
          <td>{{ row.uuid }}</td>
          <td>{{ row.rssi}}</td>
          <td>{{ row.rssiFiltered}}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>

export default {
  name: 'RawDatabaseTable',
  props: ['table'],
  data() {

  },
  methods: {

  },
};
</script>
