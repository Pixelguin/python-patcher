'use strict';

let app = null;

// <python-pather-rest-lib.js should be included before this file>
// TODO: use proper javascript import
// When the main window is loaded
// - Vue components are defined
// - Main Vue instance, called 'app', is initialized
// - the subModHandles are retrieved from the python server to populate the app.subModList property
window.onload = function onWindowLoaded() {
  Vue.component('dropdown-game-menu', {
    data() {
      let menuData = {
        families: {},
      };

      doPost('subModHandles', [], (responseData) => {
        const modNameToSubModHandleMap = {};
        responseData.subModHandles.forEach((subModHandle) => {
          modNameToSubModHandleMap[subModHandle.modName] = subModHandle;
        });

        // Sort by id
        const uniqueSubMods = Object.values(modNameToSubModHandleMap);
        uniqueSubMods.sort((a, b) => a.id - b.id);

        // group by family
        const families = _.groupBy(uniqueSubMods, subMod => subMod.family);

        // for purposes of display, umineko and umineko_nscripter are the same group.
        if (families.umineko !== undefined && families.umineko_nscripter !== undefined) {
          families.umineko = families.umineko.concat(families.umineko_nscripter);
          delete families.umineko_nscripter;
        }

        menuData.families = families;
      });

      return menuData;
    },
    methods: {
      remapFamily(familyName) {
        // For now just append "When They Cry" - if other games added, use a dictionary
        return `${familyName} When They Cry`;
      },
    },
    template: `
    <ul class="menu">
    <li class="has-dropdown" v-for='(modsInFamily, family, index) in families'>
        <a target="_self">{{ remapFamily(family) }}</a>
        <ul>
            <li v-for='num in modsInFamily'><a onclick="setModNameAndNavigate('Umineko Question (Ch. 1-4)')">{{ num.modName }}</a></li>
        </ul>
    </li>
    </ul>
    `,
  });

  app = new Vue({
    el: '#app',
    data: {
      uniqueSubMods: [],
      subModExtraProperties: {
        'Umineko Question (Ch. 1-4)': {
          img: 'img/games/umineko-question.jpg',
          dataFilter: 'Question Arcs',
        },
        'Umineko Answer (Ch. 5-8)': {
          img: 'img/games/umineko-answer.jpg',
          dataFilter: 'Answer Arcs',
        },
        'Umineko Hane': {
          img: 'img/games/umineko-hane.png',
          dataFilter: 'Answer Arcs',
        },
        'Console Arcs': {
          img: 'img/games/console.jpg',
          dataFilter: 'Console Arcs',
        },
        'Onikakushi Ch.1': {
          img: 'img/games/header1.jpg',
          dataFilter: 'Question Arcs',
        },
        'Watanagashi Ch.2': {
          img: 'img/games/header2.jpg',
          dataFilter: 'Question Arcs',
        },
        'Tatarigoroshi Ch.3': {
          img: 'img/games/header3.jpg',
          dataFilter: 'Question Arcs',
        },
        'Himatsubushi Ch.4': {
          img: 'img/games/header4.jpg',
          dataFilter: 'Question Arcs',
        },
        'Meakashi Ch.5': {
          img: 'img/games/header5.jpg',
          dataFilter: 'Answer Arcs',
        },
        'Tsumihoroboshi Ch.6': {
          img: 'img/games/header6.jpg',
          dataFilter: 'Answer Arcs',
        },
      },
      // Data filters are defined manually so you can set the order
      dataFilters: ['Question Arcs', 'Answer Arcs', 'Console Arcs'],
      currentDataFilter: null,
      masonryInitialized: false,
    },
    methods: {
      nav(gameName) {
        setModNameAndNavigate(gameName);
      },
    },
    computed: {

    },
    watch: {

    },
    updated() {
      // call initializeMasonry() from the theme's javascript js/script.js, on the first update call
      if (!this.masonryInitialized) {
        this.masonryInitialized = true;
        initializeMasonry();
        console.log("initing masonry");
      }
    },
    created() {
      // populate the app.subModList with subMods from the python server
      doPost('subModHandles', [], (responseData) => {
        const modNameToSubModHandleMap = {};
        console.log(responseData);
        responseData.subModHandles.forEach((subModHandle) => {
          modNameToSubModHandleMap[subModHandle.modName] = subModHandle;
        });

        app.uniqueSubMods = Object.values(modNameToSubModHandleMap);
        app.uniqueSubMods.sort((a, b) => a.id - b.id);
        console.log(app.uniqueSubMods);

        //add image url to each submod
      });

      setTimeout(() => {
          replaceElementWithNews('globalNews', 'news');
          replaceElementWithBuildInfo('build-info');
          replaceDonationStatus('donationMonthsRemaining', 'donationProgress');
      }, 500);
    },
  });


};
