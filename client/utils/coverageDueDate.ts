import moment from 'moment';
import {IEventItem, IPlanningItem} from 'superdesk-planning/client/interfaces';
import {eventUtils, timeUtils} from 'superdesk-planning/client/utils';

export const getEventDateContext = (eventItem?: IEventItem, planningItem?: IPlanningItem) => {
    const tz = eventItem?.dates?.tz;
    const fallback = moment(planningItem?.planning_date);

    const toEventTz = (value?: moment.MomentInput) =>
        value && tz ? timeUtils.getDateInRemoteTimeZone(value as moment.Moment, tz) : fallback.clone();

    const start = toEventTz(eventItem?.dates?.start);
    const end = toEventTz(eventItem?.dates?.end);

    const isAllDay =
        !!eventItem?.dates?.all_day ||
        (!!eventItem?.dates?.start &&
            !!eventItem?.dates?.end &&
            eventUtils.isEventAllDay(start, end, true));

    return {start, end, isAllDay};
};

export const getCoverageDueDate = (
    planningItem: IPlanningItem,
    eventItem?: IEventItem,
): moment.Moment | null => {
    const {end, isAllDay} = getEventDateContext(eventItem, planningItem);
    let coverageTime: moment.Moment | null = null;

    if (eventItem && isAllDay) {
        coverageTime = end.clone();
        coverageTime.set('hour', 20);
        coverageTime.set('minute', 0);
        coverageTime.set('second', 0);
    } else if (eventItem && eventItem._time_to_be_confirmed) {
        coverageTime = end.clone();
        coverageTime.set('hour', 20);
        coverageTime.set('minute', 0);
        coverageTime.set('second', 0);
    } else if (eventItem) {
        coverageTime = end.clone();
        coverageTime.add(1, 'hour');
        if (!coverageTime.isSame(end, 'day')) {
            // make sure we're not going into the next day
            coverageTime = end.clone();
        }
    } else if (planningItem) {
        coverageTime = moment(planningItem.planning_date);
    }

    return coverageTime;
};
