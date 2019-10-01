
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
            {name: 'DE', id: 'de'},
            {name: 'FR', id: 'fr'},
            {name: 'EN', id: 'en'},
            {name: 'ES', id: 'es'},
            {name: 'NL', id: 'nl'},
        ];

        this.types = [
            {name: 'alert', id: 'alert'},
            {name: 'text', id: 'text'},
            {name: 'brief', id: 'brief'}
        ]

        this.periods = [
            {name: 'Whenever', id: ''},
            {name: 'Last 4 hours', id: 'last4h'},
            {name: 'Last 8 hours', id: 'last8h'},
            {name: 'Today', id: 'today'},
            {name: 'Yesterday', id: 'yesterday'},
            {name: 'Last 24 hours', id: 'day'},
            {name: 'Last 48 hours', id: 'last48h'},
            {name: 'Last 72 hours', id: 'last74h'},
            {name: 'Last week', id: 'week1'},
            {name: 'Last 2 weeks', id: 'week2'},
            {name: 'Last month', id: 'month'},
            {name: 'Last year', id: 'year'},
            {name: 'Last 2 years', id: 'year2'},
        ];
    }
}
