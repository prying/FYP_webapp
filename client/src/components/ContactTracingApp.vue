<template>
  <div class="container">
    <div style="width: 100%; overflow: hidden;">
      <div style="width: 70%;">
        <div>
          <h2>Room tracking</h2>
        </div>
        <div style="width: 100%; float: left; overflow-y: scroll; height:300px;">
          <DatabaseTable v-if="showRoomTable" :table="table"/>
          <RawDatabaseTable v-else :table="rawTable" />
        </div>
      </div>
     <div style="margin-left: 70%;">
       <div style="margin-left: 1.5em;">
        <DatabaseInput @submitedQuery="submitQuery" @showRaw="showRaw"/>
       </div>
      </div>
    </div>
    <ContactTable :table="contactTable" style="padding-top:5%"/>
  </div>
</template>

<script>
import axios from 'axios';
import DatabaseTable from './DatabaseTable.vue';
import ContactTable from './ContactTable.vue';
import DatabaseInput from './Input.vue';
import RawDatabaseTable from './RawDatabaseTable.vue';

export default {
  name: 'TracingApp',
  components: {
    DatabaseTable,
    ContactTable,
    DatabaseInput,
    RawDatabaseTable,
  },
  data() {
    return {
      table: [],
      rawTable: [],
      contactTable: [],
      showRoomTable: true,
    };
  },
  methods: {
    getDatabaseResponse() {
      const path = 'http://159.196.72.33:5000/query';
      axios.get(path)
        .then((res) => {
          this.table = res.data.roomTable;
          this.rawTable = res.data.rawTable;
          this.contactTable = res.data.contactList;
          // eslint-disable-next-line
          // console.log(this.table);
        })
        .catch((err) => {
          // eslint-disable-next-line
          console.log(err);
        });
    },
    submitQuery(queryData) {
      const path = 'http://159.196.72.33:5000/query';
      const payload = {
        deviceID: queryData.deviceID,
        date: queryData.date,
      };
      axios.post(path, payload)
        .then(() => {
          this.getDatabaseResponse();
        })
        .catch((err) => {
          // eslint-disable-next-line
          console.log(err);
          this.getDatabaseResponse();
        });
    },
    showRaw(showRawData) {
      this.showRoomTable = !showRawData;
    },
  },
};
</script>
