<template>
  <v-app>
    <v-app-bar app color="blue" dark>
      <v-toolbar-title>
        <h1>gaqqie - Quantum Computer Cloud Service</h1>
      </v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-row>
        <v-col cols="2">
          <v-navigation-drawer permanent>
            <v-list nav dense>
              <v-list-item-group>
                <v-list-item link>
                  <router-link to="/jobs">Jobs</router-link>
                </v-list-item>
                <v-list-item link>
                  <router-link to="/devices">Devices</router-link>
                </v-list-item>
                <v-list-item link>
                  <router-link to="/providers">Providers</router-link>
                </v-list-item>
              </v-list-item-group>
            </v-list>
          </v-navigation-drawer>
        </v-col>
        <router-view />
      </v-row>
    </v-main>
  </v-app>
</template>

<style lang="scss">
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
