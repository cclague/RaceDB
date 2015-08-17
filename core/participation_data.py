
import datetime
import utils
from collections import defaultdict
from models import *

def participation_data( year=None, discipline=None, race_class=None ):
	competitions = Competition.objects.all()
	if year is not None:
		competitions = competitions.filter( start_date__year = year )
	if discipline is not None:
		competitions = competitions.filter( discipline = discipline )
	if race_class is not None:
		competitions = competitions.filter( race_class = race_class )
	
	data = []
	license_holders_count = defaultdict( int )
	license_holders_men_count = defaultdict( int )
	license_holders_women_count = defaultdict( int )
	age_count = defaultdict( int )
	age_men_count = defaultdict( int )
	age_women_count = defaultdict( int )
	
	category_count_overall = defaultdict( int )
	category_competition_count = defaultdict( lambda: defaultdict(int) )
	event_competition_count = defaultdict( lambda: defaultdict(int) )
	competition_count_total = defaultdict( int )
	
	competition_category_event = defaultdict( dict )
	
	age_increment = 5
	age_range_license_holders = [set() for i in xrange(0, 120, age_increment)]
	age_range_participant_count = [0 for i in xrange(0, 120, age_increment)]
	age_range_men_license_holders = [set() for i in xrange(0, 120, age_increment)]
	age_range_men_participant_count = [0 for i in xrange(0, 120, age_increment)]
	age_range_women_license_holders = [set() for i in xrange(0, 120, age_increment)]
	age_range_women_participant_count = [0 for i in xrange(0, 120, age_increment)]
	license_holders_set = set()
	
	personas = defaultdict( int )
	
	profile_year = 0
	num_competitions, num_events = 0, 0
	for competition in competitions.order_by( 'start_date' ):
		if not competition.has_participants():
			continue
		
		num_competitions += 1
		profile_year = max( profile_year, competition.start_date.year )
		
		competition_data = {
			'name': competition.name,
			'start_date': competition.start_date.strftime('%Y-%m-%d'),
			'events': [],
			'men': 0,
			'women': 0,
			'total': 0,
		}
		for event in competition.get_events():
			if not event.has_participants():
				continue
				
			num_events += 1
			
			participant_data = []
			for participant in event.get_participants():
				age = event.date_time.year - participant.license_holder.date_of_birth.year
				category_name = participant.category.code_gender if participant.category else unicode(_('Unknown'))
				
				participant_data.append( [participant.license_holder.gender, age] )
				license_holders_set.add( participant.license_holder )
				license_holders_count[participant.license_holder] += 1
				age_count[age] += 1
				
				age_range_license_holders[age//age_increment].add( participant.license_holder )
				age_range_participant_count[age//age_increment] += 1
				
				category_count_overall[category_name] += 1
				category_competition_count[competition][category_name] += 1
				event_competition_count[competition][event] += 1
				competition_count_total[competition] += 1
				
				personas[(category_name, age - age%age_increment)] += 1
				competition_category_event[competition][category_name] = event.name
				
				if participant.license_holder.gender == 0:
					license_holders_men_count[participant.license_holder] += 1
					age_men_count[age] += 1
					age_range_men_license_holders[age//age_increment].add( participant.license_holder )
					age_range_men_participant_count[age//age_increment] += 1
				else:
					license_holders_women_count[participant.license_holder] += 1
					age_women_count[age] += 1
					age_range_women_license_holders[age//age_increment].add( participant.license_holder )
					age_range_women_participant_count[age//age_increment] += 1
			
			event_data = {
				'name':event.name,
				'participants':participant_data,
				'men': sum(1 for p in participant_data if p[0] == 0),
				'women': sum(1 for p in participant_data if p[0] == 1),
			}
			event_data['total'] = event_data['men'] + event_data['women']
			competition_data['men'] += event_data['men']
			competition_data['women'] += event_data['women']
			competition_data['events'].append( event_data )
		
		competition_data['total'] = competition_data['men'] + competition_data['women']
		data.append( competition_data )
	
	age_range_average = [
		0 if not age_range_license_holders[i] else age_range_participant_count[i] / float(len(age_range_license_holders[i]))
		for i in xrange(len(age_range_participant_count))
	]
	age_range_men_average = [
		0 if not age_range_men_license_holders[i] else age_range_men_participant_count[i] / float(len(age_range_men_license_holders[i]))
		for i in xrange(len(age_range_men_participant_count))
	]
	age_range_women_average = [
		0 if not age_range_women_license_holders[i] else age_range_women_participant_count[i] / float(len(age_range_women_license_holders[i]))
		for i in xrange(len(age_range_women_participant_count))
	]
	
	def trim_right_zeros( a ):
		for i in xrange(len(a)-1, -1, -1):
			if a[i]:
				del a[i+1:]
				break
	
	trim_right_zeros( age_range_average )
	trim_right_zeros( age_range_men_average )
	trim_right_zeros( age_range_women_average )
	
	license_holder_profile = []
	license_holder_men_profile = []
	license_holder_women_profile = []
	if profile_year:
		license_holder_profile = sorted(profile_year - lh.date_of_birth.year for lh in license_holders_set)
		license_holder_men_profile = sorted(profile_year - lh.date_of_birth.year for lh in license_holders_set if lh.gender == 0)
		license_holder_women_profile = sorted(profile_year - lh.date_of_birth.year for lh in license_holders_set if lh.gender == 1)
	else:
		profile_year = datetime.date.today().year
		
	participants_total = sum(c['total'] for c in data)
	
	def format_int_percent( num, total ):
		return {'v':num, 'f':'{} / {} ({:.2f}%)'.format(num, total, (100.0 * num) / (total or 1))}
	
	def format_int_percent_event( num, total, event ):
		return {'v':num, 'f':'{} / {} ({:.2f}%) - {}'.format(num, total, (100.0 * num) / (total or 1), event)}
	
	category_count = [['Category', 'Total']] + sorted( ([k, v] for k, v in category_count_overall.iteritems()), key=lambda x: x[1], reverse=True )
	ccc = [['Competition'] + [name for name, count in category_count[1:]]]
	for competition in sorted( (category_competition_count.iterkeys()), key=lambda x: x.start_date ):
		ccc.append( [competition.name] +
			[format_int_percent_event(
					category_competition_count[competition].get(name, 0),
					competition_count_total[competition],
					competition_category_event.get(competition,{}).get(name,''),
				) for name, count in category_count[1:]] )
		
	# Add cumulative percent.
	category_count[0].append( 'Cumulative %' )
	cumulativePercent = 0.0
	for c in category_count[1:]:
		cumulativePercent += 100.0*c[-1] / participants_total
		c.append( cumulativePercent )
	
	event_max = max(len(events) for events in event_competition_count.itervalues()) if event_competition_count else 0
	eee = [['Competition'] + ['{}'.format(i+1) for i in xrange(event_max)]]
	for competition in sorted( (event_competition_count.iterkeys()), key=lambda x: x.start_date ):
		events = sorted( ((event, count) for event, count in event_competition_count[competition].iteritems()), key=lambda x: x[0].date_time )
		participant_max = sum( e[1] for e in events )
		eee.append( [competition.name] + [format_int_percent_event(events[i][1], participant_max, events[i][0].name)
			if i < len(events) else 0 for i in xrange(event_max)] )
	
	personas = sorted(
		([cat, '{}-{}'.format(age,age+age_increment-1), count, (100.0*count)/float(participants_total)] for (cat, age), count in personas.iteritems()),
		key=lambda x:x[-1],
		reverse=True,
	)
	for p in personas:
		p[3] = {'v':p[3],'f':'{:.2f}'.format(p[3])}
	personas = [['Category', 'Age', 'Count', 'Percent']] + personas
	
	def get_expected_age( ac ):
		if not ac:
			return None
		most_frequent = max( v for v in ac.itervalues() )
		for a, c in ac.iteritems():
			if c == most_frequent:
				return a
		return None
	
	payload = {
		'num_competitions': num_competitions,
		'num_events': num_events,
		
		'participants_total': participants_total,
		'participants_men_total': sum(c['men'] for c in data),
		'participants_women_total': sum(c['women'] for c in data),
		
		'license_holders_total': len(license_holders_count),
		'license_holders_men_total': len(license_holders_men_count),
		'license_holders_women_total': len(license_holders_women_count),
		
		'events_average': sum(v for v in license_holders_count.itervalues()) / (float(len(license_holders_count)) or 1),
		'events_men_average': sum(v for v in license_holders_men_count.itervalues()) / (float(len(license_holders_men_count)) or 1),
		'events_women_average': sum(v for v in license_holders_women_count.itervalues()) / (float(len(license_holders_women_count)) or 1),
		
		'expected_age': get_expected_age(age_count),
		'expected_men_age': get_expected_age(age_men_count),
		'expected_women_age': get_expected_age(age_women_count),
		
		'age_range_average':age_range_average,
		'age_range_men_average':age_range_men_average,
		'age_range_women_average':age_range_women_average,
		'age_increment': age_increment,
		
		'profile_year':profile_year,
		'license_holder_profile':license_holder_profile,
		'license_holder_men_profile':license_holder_men_profile,
		'license_holder_women_profile':license_holder_women_profile,
		
		'category_count':category_count,
		'category_competition_count':ccc,
		'event_competition_count':eee,
		
		'personas':personas[:10],
		
		'competitions': data,
	}
	return payload
