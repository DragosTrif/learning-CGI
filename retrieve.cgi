#!/usr/bin/perl -w

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $query = CGI->new();

my $search_name;
my $guest_file = 'images/guest.txt';

&print_page_start;

if ($query->param()) {
	&search_name_result;
} else {
	&print_form;	
}
&print_page_end;

chomp $@;
if ($@) {
	print "<p>ERROR: $@</p>\n";
}

sub print_page_start {
	print $query->header;
	print "<html>\n<head><title>Search for records</title></head>\n";
	print "<head>\n<body>\n";
	print "<h1>Search for records</h1>\n";
}

sub print_page_end {
	print "</body></html>\n";
}

sub search_name_result {
	my $search_name = $query->param('name');
	
	eval {
		open (GUEST, "<", $guest_file) or die "Can’t open $guest_file: $!";
		while (my $line = <GUEST>) {
			chomp $line;
			my ($name, $email, $browser) = split /:/, $line;
			
			if ($search_name =~ /$name/) {
				print "<p>\n";
				print "$name<br />\n$email<br />\n";
				print "$browser<br/ >\n<hr />\n";
				print "</p>\n";
			}
		}
	}
}

sub print_form {
	print "<form action=\"retrieve.cgi\"  >\n";
	print "<input type=\"text\" name=\"name\" /><br />\n";
	print "<input type='submit' value='Submit'/>\n";
	print "</form>\n";
}
