#!/usr/bin/perl -wT

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $query = new CGI;
my $voter;

# Determine whether the user is of legal voting age.
# Import the CGI module and create a query object to retrieve the
# form input.
# Determine whether the user is of legal voting age.
if ($query->param('age') >= 18) {
	$voter = 'yes';
}
else {
	$voter = 'no';
}
# Print out a message indicating whether the user is
# a registered voter or not.
print $query->header;
print "<html><head><title>Voting Age Check</title></head>\n";
print "<body>\n";
print "<h1>Voting Age Check</h1>\n";
if ($voter eq 'yes') {
	print "<p>You are old enough to vote.</p>\n";
}
else {
	print "<p>You are not yet old enough to vote.</p>\n";
}
print "</body></html>\n"
