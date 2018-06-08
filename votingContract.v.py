voters: public({
	weight: int128,
	voted: bool,
	delegate: address,
	vote: int128
}[address])

proposals: public({
	name: bytes32,
	vote_count: int128
} [int128])

voter_count: public(int128)
chairperson: public(address)
int128_proposals: public(int128)

@public
@constant
def delegated(addr: address) -> bool:
	return not not self.voters[addr].delegate

@public
@constant
def directly_voted(addr: address) -> bool:
	return self.voters[addr].voted and not self.voters[addr].delegate

@public
def __init__(_proposalNames: bytes32[2]):
	self.chairperson = msg.sender
	self.voter_count = 0
	for i in range(2):
		self.proposals[i] = {
			name: _proposalNames[i],
			vote_count: 0
		}
		self.int128_proposals += 1

@public
def give_right_to_vote(voter: address):
	assert msg.sender == self.chairperson
	assert not self.voters[voter].voted
	assert self.voters[voter].weight == 0
	self.voters[voter].weight = 1
	self.voter_count += 1

@public
def forward_weight(delegate_with_weight_to_forward: address):
    assert self.delegated(delegate_with_weight_to_forward)
    assert self.voters[delegate_with_weight_to_forward].weight > 0

    target: address = self.voters[delegate_with_weight_to_forward].delegate
    for i in range(4):
        if self.delegated(target):
            target = self.voters[target].delegate
            assert target != delegate_with_weight_to_forward
        else:
            # Weight will be moved to someone who directly voted or
            # hasn't voted.
            break

    weight_to_forward: int128 = self.voters[delegate_with_weight_to_forward].weight
    self.voters[delegate_with_weight_to_forward].weight = 0
    self.voters[target].weight += weight_to_forward

    if self.directly_voted(target):
        self.proposals[self.voters[target].vote].vote_count += weight_to_forward
        self.voters[target].weight = 0

@public
def delegate(to: address):
	assert not self.voters[msg.sender].voted
	assert to != msg.sender and not not to
	self.voters[msg.sender].voted = True
	self.voters[msg.sender].delegate = to
	self.forward_weight(msg.sender)

@public
@constant
def winning_proposal() -> int128:
	winning_vote_count: int128 = 0
	winning_proposal: int128 = 0
	for i in range(2):
		if self.proposals[i].vote_count > winning_vote_count:
			winning_vote_count = self.proposals[i].vote_count
			winning_proposal = i
	return winning_proposal

@public
@constant
def winner_name() -> bytes32:
	return self.proposals[self.winning_proposal()].name
