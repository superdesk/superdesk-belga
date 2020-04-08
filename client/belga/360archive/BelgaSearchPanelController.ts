interface Subject {
  id: string;
  name: string;
}

export default class BelgaSearchPanelController {
  languages: Array<Subject>;
  periods: Array<Subject>;
  types: Array<Subject>;

  $onInit() {
    this.languages = [
      { name: "DE", id: "de" },
      { name: "FR", id: "fr" },
      { name: "EN", id: "en" },
      { name: "ES", id: "es" },
      { name: "NL", id: "nl" }
    ];

    this.types = [
      { name: "Alert", id: "Alert" },
      { name: "Text", id: "Text" },
      { name: "Brief", id: "Brief" },
      { name: "Short", id: "Short" }
    ];

    this.periods = [
      { name: "Whenever", id: "" },
      { name: "Last 24 hours", id: "day" },
      { name: "Last week", id: "week" },
      { name: "Last month", id: "month" },
      { name: "Last year", id: "year" },
    ];
  }
}
