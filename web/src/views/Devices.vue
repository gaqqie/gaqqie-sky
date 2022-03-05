<template>
  <v-col>
    <v-row class="pt-10" justify="center"><h1>Devices</h1></v-row>
    <v-row class="" justify="end">
      <v-col offset-md="10">
        <v-btn class="elevation-1" color="white" @click="getDevices()" small>
          <v-icon>mdi-reload</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row class="" justify="center">
      <v-col cols="11">
        <v-data-table
          :headers="headers"
          :items="devices"
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
                  getDeviceByName(item.name);
                  getDeviceImageByName(name);
                "
              >
                <td align="left">{{ item.name }}</td>
                <td align="left">{{ item.provider_name }}</td>
                <td align="justify">{{ item.status }}</td>
                <td align="justify">{{ item.device_type }}</td>
                <td align="right">{{ item.num_qubits }}</td>
                <td align="right">{{ item.max_shots }}</td>
                <td align="left">{{ item.description }}</td>
              </tr>
            </tbody>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row class="pr-5">
      <v-col>
        <v-card class="px-10" justify="center">
          <v-card-title class="text-h4">{{ device.name }}</v-card-title>
          <v-row class="pl-3">
            <div>Common properties</div>
          </v-row>
          <v-row>
            <v-col cols="3">
              <v-data-table
                dense
                :headers="common_properties_header"
                :items="device.details.common_properties"
                hide-default-header
                hide-default-footer
                class="elevation-1 noborder"
              ></v-data-table>
            </v-col>
            <v-col>
              <v-card-text class="text-left">
                <div class="text-subtitle-1">
                  {{ device.details.detail_description }}
                </div>
              </v-card-text>
            </v-col>
          </v-row>
          <v-row class="pl-3">
            <div>Device specific properties</div>
          </v-row>
          <v-row>
            <v-col cols="5">
              <v-data-table
                dense
                :headers="specific_properties_header"
                :items="device.details.specific_properties"
                hide-default-header
                hide-default-footer
                class="elevation-1 noborder"
              ></v-data-table>
            </v-col>
          </v-row>
          <v-row class="pl-3">
            <div>Topology</div>
          </v-row>
          <v-row class="pl-3">
            <v-img
              max-height="400"
              max-width="800"
              src="../assets/topology.png"
            ></v-img>
          </v-row>
          <v-row class="pl-3">
            <div>Caliblation data (1qubit)</div>
          </v-row>
          <v-row>
            <v-col>
              <v-data-table
                dense
                :headers="calibration_1q_header"
                :items="device.details.calibration_1q"
                hide-default-footer
                class="elevation-1 noborder"
              ></v-data-table>
            </v-col>
          </v-row>
          <v-row class="pl-3">
            <div>Caliblation data (2qubits connection)</div>
          </v-row>
          <v-row>
            <v-col>
              <v-data-table
                dense
                :headers="calibration_2q_header"
                :items="device.details.calibration_2q"
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
const urlGetDevices =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/devices";
const urlGetDeviceByName =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/devices/{name}";
const urlGetDeviceImageByName =
  "https://" +
  apiId +
  ".execute-api." +
  region +
  ".amazonaws.com/" +
  stage +
  "/v1/devices/{name}/image";

export default {
  name: "Devices",

  data: () => ({
    // devices table
    headers: [
      {
        text: "Device name",
        align: "start",
        value: "name",
      },
      { text: "Provider name", value: "provider_name" },
      { text: "Status", value: "status" },
      { text: "Type", value: "device_type" },
      { text: "Qubits", value: "num_qubits" },
      { text: "Max shots", value: "max_shots" },
      { text: "Description", value: "description" },
    ],
    devices: [],

    // device detail
    common_properties_header: [
      { text: "name", value: "name" },
      { text: "value", value: "value" },
    ],
    specific_properties_header: [
      { text: "name", value: "name" },
      { text: "value", value: "value" },
    ],
    device: {
      details: {
        detail_description: "",
        common_properties: [],
        specific_properties: [],
        calibration_1q: [],
        calibration_2q: [],
      },
    },
    details: {},

    // calibration 1q table in device detail
    calibration_1q_header: [
      { text: "Qubit", value: "qubit" },
      { text: "T1 (μs)", value: "T1" },
      { text: "T2 (μs)", value: "T2" },
      { text: "Fidelity (%)", value: "fidelity" },
      { text: "Readout Fidelity (%)", value: "readout" },
    ],

    // calibration 2q table in device detail
    calibration_2q_header: [
      { text: "Qubit pair", value: "qubits" },
      { text: "CX Gate Fidelity (%)", value: "fidelity_cx" },
    ],
  }),
  methods: {
    getDevices() {
      axios.get(urlGetDevices).then(async (response) => {
        var devices = [];
        for (let row of response.data) {
          devices.push(row);
        }
        this.devices = devices;
      });
    },
    getDeviceByName(name) {
      var url = urlGetDeviceByName.replace("{name}", name);
      axios({
        url: url,
        method: "GET",
      }).then((response) => {
        this.device = response.data;
      });
    },
    getDeviceImageByName(name) {
      var url = urlGetDeviceImageByName.replace("{name}", name);
      axios({
        url: url,
        method: "GET",
      }).then((response) => {
        response.data;
        //this.device = response.data;
      });
    },
  },
  mounted: function () {
    document.title = "gaqqie - Quantum Computer Cloud Service";
    this.getDevices();
  },
};
</script>
