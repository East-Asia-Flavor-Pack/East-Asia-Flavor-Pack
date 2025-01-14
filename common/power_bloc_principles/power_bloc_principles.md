﻿	principle_key = {
		visible = { trigger }		# Determines whether the principle is visible in the list when forming a power bloc.
		possible = { trigger }		# Determines whether the principle is selectable in the list when forming a power bloc.
		incompatible_with = other_principle_key	# Can be repeated. Other principles referenced in this way are incompatible with this principle.
		icon = <texture path>					# Icon
		background = <texture path>				# Background
		power_bloc_modifier = {}	# This modifier is added to the power bloc
		participant_modifier = {}	# This modifier is added to the leader and every member of the power bloc
		leader_modifier = {}		# This modifier is added to the leader of the power bloc
		member_modifier = {}		# This modifier is added to every member of the power bloc except the leader
		institution = institution_key 			# Which institution it add additional modifiers to
		institution_modifier = {}				# Modifiers that the principle provides the institution with
	}
