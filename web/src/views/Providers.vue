<template>
  <v-col>
    <v-row class="pt-10" justify="center"><h1>Providers</h1></v-row>
    <v-row class="" justify="end">
      <v-col offset-md="10">
        <v-btn class="elevation-1" color="white" @click="getProviders()" small>
          <v-icon>mdi-reload</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row class="" justify="center">
      <v-col cols="11">
        <v-data-table
          :headers="headers"
          :items="providers"
          :items-per-page="10"
          hide-default-footer
          multi-sort
          :sort-by="['name']"
          class="elevation-1"
        >
          <template v-slot:body="{ items }">
            <tbody>
              <tr
                v-for="item in items"
                :key="item.name"
                @click="
                  getProviderDetail(item.name);
                  getDeviceByProviderName(item.name);
                "
              >
                <td align="left">{{ item.name }}</td>
                <td align="justify">{{ item.status }}</td>
                <td align="left">{{ item.description }}</td>
              </tr>
            </tbody>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row class="pr-5">
      <v-col cols="12">
        <v-card class="px-10" justify="center">
          <v-card-title class="text-h4">{{ provider.name }}</v-card-title>
          <v-row class="pl-3">
            <div>Common properties</div>
          </v-row>
          <v-row>
            <v-col cols="3">
              <v-data-table
                dense
                :headers="common_properties_header"
                :items="provider.details.common_properties"
                hide-default-header
                hide-default-footer
                class="elevation-1 noborder"
              ></v-data-table>
            </v-col>
            <v-col>
              <v-card-text class="text-left">
                <div class="text-subtitle-1">
                  {{ provider.details.detail_description }}
                </div>
              </v-card-text>
            </v-col>
          </v-row>
          <v-row class="pl-3">
            <div>Provider specific properties</div>
          </v-row>
          <v-row>
            <v-col cols="5">
              <v-data-table
                dense
                :headers="specific_properties_header"
                :items="provider.details.specific_properties"
                hide-default-header
                hide-default-footer
                class="elevation-1 noborder"
              ></v-data-table>
            </v-col>
          </v-row>
          <v-row class="pl-3">
            <div>Devices</div>
          </v-row>
          <v-row>
            <v-col>
              <v-data-table
                dense
                :headers="device_headers"
                :items="devices"
                hide-default-footer
                class="elevation-1 noborder"
              ></v-data-table>
            </v-col>
          </v-row>
        </v-card>
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
const urlGetProviders =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/providers";
const urlGetProviderByName =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/providers/{name}";
const urlGetDeviceByProviderName =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/devices/provider/{provider_name}";

export default {
  name: "Providers",

  data: () => ({
    // prodivers table
    headers: [
      {
        text: "Provider name",
        align: "start",
        value: "name",
      },
      { text: "Status", value: "status" },
      { text: "Description", value: "description" },
    ],
    providers: [],

    // prodiver detail
    common_properties_header: [
      { text: "name", value: "name" },
      { text: "value", value: "value" },
    ],
    specific_properties_header: [
      { text: "name", value: "name" },
      { text: "value", value: "value" },
    ],
    provider: {
      name: "IBM",
      details: {
        detail_description:
          "IBM quantum processors are universal, gate-model machines based on superconducting qubit.",
        common_properties: [
          {
            name: "Status",
            value: "ACTIVE",
          },
        ],
        specific_properties: [
          {
            name: "Requirements",
            value: "need IBM Q accunt",
          },
        ],
      },
    },

    // device table in prodiver detail
    device_headers: [
      {
        text: "Device name",
        align: "start",
        value: "name",
      },
      { text: "Status", value: "status" },
      { text: "Type", value: "device_type" },
      { text: "Qubits", value: "num_qubits" },
      { text: "Max shots", value: "max_shots" },
      { text: "Description", value: "description" },
    ],
    devices: [
      {
        name: "ibmq_montreal",
        status: "ACTIVE",
        device_type: "QPU",
        num_qubits: 27,
        max_shots: 8192,
        description: "This is a real machine.",
      },
      {
        name: "ibmq_manhattan",
        status: "ACTIVE",
        device_type: "QPU",
        num_qubits: 65,
        max_shots: 8192,
        description: "This is a real machine.",
      },
      {
        name: "ibmq_santiago",
        status: "ACTIVE",
        device_type: "QPU",
        num_qubits: 5,
        max_shots: 8192,
        description: "This is a real machine.",
      },
    ],
  }),
  methods: {
    getStatusColor(status) {
      if (status == "RUNNING") return "red";
      else if (status > 200) return "orange";
      else return "green";
    },
    getProviders() {
      axios.get(urlGetProviders).then(async (response) => {
        var providers = [];
        for (let row of response.data) {
          providers.push(row);
        }
        this.providers = providers;
      });
    },
    getProviderDetail(name) {
      var url = urlGetProviderByName.replace("{name}", name);
      axios({
        url: url,
        method: "GET",
      }).then((response) => {
        this.provider = response.data.details;
      });
    },
    getDeviceByProviderName(provider_name) {
      var url = urlGetDeviceByProviderName.replace(
        "{provider_name}",
        provider_name
      );
      axios({
        url: url,
        method: "GET",
      }).then((response) => {
        this.devices = response.data;
      });
    },
  },
  mounted: function () {
    document.title = "gaqqie - Quantum Computer Cloud Service";
    this.getProviders();
    this.getProviderDetail("IBM");
  },
};
</script>
