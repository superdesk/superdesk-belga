
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
            {id: 'news', name: 'News'},
            {id: 'sports', name: 'Sports'},
            {id: 'entertainment', name: 'Entertainment'},
            {id: 'royals', name: 'Royals'},
            {id: 'portraits', name: 'Portraits'},
            {id: 'archives', name: 'Archives'},
            {id: 'creative', name: 'Documentary'},
        ];

        this.sources = [
            {name: 'Belga', id: 'BELGA'},
            {name: 'AFP', id: 'AFP'},
        ];

        this.periods = [
            {name: 'Whenever', id: ''},
            {name: 'Today', id: 'today'},
            {name: 'Yesterday', id: 'yesterday'},
            {name: 'Last week', id: 'week1'},
            {name: 'Last 2 weeks', id: 'week2'},
            {name: 'Last month', id: 'month'},
            {name: 'Last year', id: 'year'},
            {name: 'Last 2 years', id: 'year2'},
        ];
    }
}
