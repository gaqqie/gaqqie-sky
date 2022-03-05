<template>
  <v-col>
    <v-row class="pt-10" justify="center">
      <h1>Jobs</h1>
    </v-row>
    <v-row class="" justify="end">
      <v-col offset-md="10">
        <v-btn class="elevation-1" color="white" @click="getJobs()" small>
          <v-icon>mdi-reload</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row class="" justify="center">
      <v-col cols="11">
        <v-data-table
          :headers="headers"
          :items="jobs"
          :items-per-page="-1"
          multi-sort
          :sort-by="['create_time']"
          :sort-desc="['true']"
          class="elevation-1"
        >
          <template v-slot:[`item.cancel`]="{ item }">
            <template v-if="item.status == 'QUEUED'">
              <v-icon class="mr-2" color="red" @click="cancelJobById(item.id)">
                mdi-cancel
              </v-icon>
            </template>
          </template>
          <template v-slot:[`item.download`]="{ item }">
            <template v-if="item.status == 'SUCCEEDED'">
              <v-icon class="mr-2" @click="getResultByJobId(item.id)">
                mdi-download
              </v-icon>
            </template>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
  </v-col>
</template>

<style>
</style>

<script>
import axios from "axios";

const apiId = "write your apiId";
const region = "ap-northeast-1";
const stage = "dev";
const urlGetJobs =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/jobs";
const urlCancelJobById =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/jobs/{id}/cancel";
const urlGetResultByJobId =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/results/{id}";

export default {
  name: "Jobs",

  data: () => ({
    headers: [
      { text: "Cancel", value: "cancel", sortable: false },
      {
        text: "Job ID",
        align: "start",
        value: "id",
      },
      //{ text: "Job name", value: "name" },
      { text: "Status", value: "status" },
      { text: "Provider", value: "provider_name" },
      { text: "Device", value: "device_name" },
      { text: "Create Time", value: "create_time" },
      { text: "End Time", value: "end_time" },
      { text: "Download", value: "download", sortable: false },
    ],
    jobs: [],
  }),
  methods: {
    getJobs() {
      axios.get(urlGetJobs).then(async (response) => {
        var jobs = [];
        for (let row of response.data) {
          if ("create_time" in row) {
            row["create_time"] = row["create_time"]
              .substring(0, 19)
              .replace("T", " ");
          }
          if ("end_time" in row) {
            row["end_time"] = row["end_time"]
              .substring(0, 19)
              .replace("T", " ");
          }
          jobs.push(row);
        }
        this.jobs = jobs;
      });
    },
    cancelJobById(job_id) {
      var url = urlCancelJobById.replace("{id}", job_id);
      axios.get(url).then(async () => {
        this.getJobs();
      });
    },
    getResultByJobId(job_id) {
      var url = urlGetResultByJobId.replace("{id}", job_id);
      axios({
        url: url,
        method: "GET",
      }).then((response) => {
        var fileURL = window.URL.createObjectURL(
          new Blob([response.data["results"]])
        );
        var fileLink = document.createElement("a");

        fileLink.href = fileURL;
        fileLink.setAttribute("download", "results.json");
        document.body.appendChild(fileLink);

        fileLink.click();
      });
    },
  },
  mounted: function () {
    document.title = "gaqqie - Quantum Computer Cloud Service";

    this.getJobs();
    //setInterval(() => {
    //  this.getJobs();
    //}, 10000);
  },
};
</script>
