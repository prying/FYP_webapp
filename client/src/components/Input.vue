<template>
  <!-- eslint-disable max-len -->
  <form>
    <div class="form-group">
      <label for="userTagID">User Tag ID:</label>
      <input type="number" class="form-control" id="userTagID" v-model="queryData.deviceID" placeholder="0">
    </div>
    <div class="form-group">
      <label for="DateSelection">Date range</label>
      <DatePicker id="DateSelection" v-model="queryData.date" range/>
    </div>
    <br>
    <div class="form-check form-switch">
      <input class="form-check-input" type="checkbox" id="flexSwitchCheckDefault" v-model="showRaw">
      <label class="form-check-label" for="flexSwitchCheckDefault">Raw data</label>
    </div>
    <br>
    <button @click="submitQuery" type="button" class="btn btn-primary" style="margin:5px;">Submit</button>
    <button @click="downloadButton" v-show="showRaw" type="button" class="btn btn-primary" style="margin:5px;">Download table</button>
  </form>
</template>

<script>
import DatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css';
// https://vue3datepicker.com/api/props/

export default {
  name: 'DatabaseInput',
  components: {
    DatePicker,
  },
  data() {
    return {
      queryData: [],
      showRaw: 0,
    };
  },
  methods: {
    submitQuery() {
      this.$emit('submitedQuery', this.queryData);
      // eslint-disable-next-line
      console.log(this.queryData.date);
      // eslint-disable-next-line
      console.log(this.queryData.date[0]);
      // eslint-disable-next-line
      console.log(this.queryData.showRaw);
    },
    downloadButton() {
      this.$emit('downloadTableButton');
    },
  },
  // Lifecycle hooks
  updated() {
    this.$emit('showRaw', this.showRaw);
  },
};
</script>
