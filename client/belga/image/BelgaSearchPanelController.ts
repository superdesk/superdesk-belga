
interface Subject {
    id: string;
    name: string;
}

export default class BelgaSearchPanelController {
    subjects : Array<Subject>;
    sources: Array<Subject>;
    periods: Array<Subject>;

    $onInit() {
        this.subjects = [
            {name: 'News', id: 'news'},
            {name: 'Sports', id: 'sports'},
            {name: 'Entertainment', id: 'entertainment'},
            {name: 'Royals', id: 'royals'},
        ];

        this.sources = [
            {name: 'Belga', id: 'BELGA'},
            {name: 'AFP', id: 'AFP'},
        ];

        this.periods = [
            {name: 'Whenever', id: ''},
            {name: 'Last hour', id: 'hour'},
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
