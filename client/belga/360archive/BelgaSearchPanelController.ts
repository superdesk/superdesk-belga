interface Subject {
  id?: string;
  name: string;
  qcode?: string;
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
      { name: "Alert",qcode: "Alert" },
      { name: "Text", qcode: "Text" },
      { name: "Brief",qcode: "Brief" },
      { name: "Short",qcode: "Short" },
      { name: "Coverage",qcode: "Coverage" },
      { name: "RelatedDocument",qcode: "RelatedDocument" },
      { name: "RelatedArticle",qcode: "RelatedArticle" },
      { name: "Audio",qcode: "Audio" },
      { name: "Picture",qcode: "Picture" },
      { name: "SMS",qcode: "SMS" },
      { name: "Video",qcode: "Video" }
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
