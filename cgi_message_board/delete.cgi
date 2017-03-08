#!/usr/bin/perl 

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $query = CGI->new();

my $topic_directory = '/tmp';
my @topics_file;
my $title;
print $query->header;
print "here we delete stuff\n";

if ($query->param('title')) {
	my $file = $query->param('file');
	chdir $topic_directory;
	unlink $file or die "Could not unlink $file: $!";
	print_success();
	
} else {
	
	find_topic();
}

print_page_end();

sub find_topic {
	chdir;
	opendir (my $dh, $topic_directory) or die "Can’t open '$topic_directory' $!:";
	my @topics_file = grep {/\.xml/} readdir($dh);
	foreach my $topic (@topics_file) {
		#print $topic,"\n";
		display_topic($topic);
	}

}

sub display_topic {
	my $topic_file = shift;

	my $topic_name;
	chdir $topic_directory;
	
	open (TOPIC, '<', "$topic_file") or die "Can't open '$topic_file' s!:";
	while (my $line = <TOPIC>) {
		if ($line =~ /<title>(.+)<\/title>/) {
			$title = $1;
			print "<form method=\"post\" action=\"delete_topic.cgi\">\n";
  			print "<input type=\"radio\" name=\"title\" value=\"$title\" > $title<br>\n";
  			print "<input type=\"hidden\" name=\"file\" value=\"$topic_file\">\n";
  			print "<input type=\"submit\" value=\"delete\" />\n";
			print "</form>\n";
		}
	}
}

sub print_success {
	print "<p>File deleted</p>\n"; 
}

sub error {
	print "<p>You must select a file </p>\n";
}

sub print_page_end {
	print "<p><a href=\"display.cgi\">view response list</a> |\n";
	print "<a href=\"post.cgi\">create new topic</a></p>\n";
	print "</body>\n</html>\n";
}
