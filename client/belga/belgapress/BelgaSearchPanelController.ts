interface Subject {
  id: string;
  name: string;
}

export default class BelgaSearchPanelController {
  languages: Array<Subject>;
  country: Array<Subject>;
  periods: Array<Subject>;
  types: Array<Subject>;

  $onInit() {
      this.languages = [
          {name: '', id: ''},
          {name: 'DE', id: 'DE'},
          {name: 'EN', id: 'EN'},
          {name: 'ES', id: 'ES'},
          {name: 'FR', id: 'FR'},
          {name: 'NL', id: 'NL'},
          {name: 'NO', id: 'NO'},
          {name: 'IT', id: 'IT'},
          {name: 'PT', id: 'PT'},
      ];

      this.country = [
          {name: 'International', id: ''},
          {name: 'Belgium', id: 'belgium'},
          {name: 'France', id: 'france'},
          {name: 'Netherlands', id: 'netherlands'},
          {name: 'Luxembour', id: 'luxembour'},
      ];

      this.types = [
          {name: '', id: ''},
          {name: 'PRINT', id: 'PRINT'},
          {name: 'ONLINE', id: 'ONLINE'},
          {name: 'SOCIAL', id: 'SOCIAL'},
          {name: 'BELGA', id: 'BELGA'},
          {name: 'MULTIMEDIA', id: 'MULTIMEDIA'},
          {name: 'OTHER', id: 'OTHER'},
      ];

      this.periods = [
          {name: 'Whenever', id: ''},
          {name: 'Today', id: 'day'},
          {name: 'Yesterday', id: 'yesterday'},
          {name: 'This week', id: 'this-week'},
          {name: 'Last week', id: 'week'},
          {name: 'Last month', id: 'month'},
          {name: 'Last year', id: 'year'},
      ];
  }
}
