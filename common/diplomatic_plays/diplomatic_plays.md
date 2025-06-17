	dp_example = {
		requires_interest_marker = yes/no # default yes
		enable_switch_sides = no # default no
		allow_negotiated_peace = yes # default yes
		mirror_war_goal = yes/no # default no
		initiator_can_add_war_goals = yes/no # default yes
		target_can_add_war_goals = yes/no # default yes
		add_infamy_for_starting_initiator_wargoals = yes/no # default yes
		add_infamy_for_starting_target_wargoals = yes/no # default no
		ai_acceptance_max = num # default NAI::DIPLOMATIC_DEMAND_ALWAYS_ACCEPT_THRESHOLD, sets an upper bound for AI acceptance for this play, which translates into a chance to accept set to a fraction of aforementioned define

		war_goal = <war goal type> 
		is_epic = yes/no
	
		texture = <texture path>
	
		selectable_in_lens = {
			# trigger here, does not contain target in scope
		}	
	
		possible = {
			# trigger here
		}

	
		on_weekly_pulse = {}
	
		on_war_begins = {}

		on_war_end = {}
		
		# no diplomatic play for demand accepted as no diplomatic play have been created
		# we use initiator as a root scope
		on_demand_accepted = {}
		
		on_demand_rejected = {}
	}