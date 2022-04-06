interface Subject {
  id?: string;
  name: string;
  qcode?: string;
}

export default class BelgaSearchPanelController {
  languages: Array<Subject>;
  periods: Array<Subject>;
  types: Array<object>;
  typesOptions: Array<object>;
  $location: any;
  $scope: any;
  $rootScope: any;
  static $inject: string[];
  constructor($scope, $location, $rootScope) {
    this.$scope = $scope;
    this.$location = $location;
    this.$rootScope = $rootScope;
    let defaultSelected = {
      "Alert": true, "Text": true, "Brief": true, "Short": true, "Coverage": true,
      "RelatedDocument": false, "RelatedArticle": false, "Audio": false, "Picture": false, "SMS": false, "Video": false
    }
    $scope.params.types = $scope.params.types ? $scope.params.types : defaultSelected;
    $rootScope.$broadcast('search:parameters');

    this.$scope.languages = [
      { name: "DE", id: "de" },
      { name: "FR", id: "fr" },
      { name: "EN", id: "en" },
      { name: "ES", id: "es" },
      { name: "NL", id: "nl" },
    ];

    this.$scope.typesOptions = [
      { name: "Alert", id: "Alert" },
      { name: "Text", id: "Text" },
      { name: "Brief", id: "Brief" },
      { name: "Short", id: "Short" },
      { name: "Coverage", id: "Coverage" },
      { name: "RelatedDocument", id: "RelatedDocument" },
      { name: "RelatedArticle", id: "RelatedArticle" },
      { name: "Audio", id: "Audio" },
      { name: "Picture", id: "Picture" },
      { name: "SMS", id: "SMS" },
      { name: "Video", id: "Video" },
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
BelgaSearchPanelController.$inject = ['$scope', '$location', '$rootScope'];