#!/usr/bin/perl

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);
use Net::SMTP;

my $query = CGI->new();
my $smtp = Net::SMTP->new('localhost');

# Set to the name of the to address
my $address = "webmaster\@rc3.org";
my $error_message = "";
my ($from, $subject, $body);

if(!$query->param()) {
	&print_page_start;
	&print_form;
	&print_page_end;
} else {
	$from = $query->param('from');
	$subject = $query->param('subject');
	$body = $query->param('body');
	&print_page_start;
	if (!&validate_form) {
		&send_email;
		&print_success;
		&print_page_end;
	} else {
		&print_page_start;
		&print_error_message;
		&print_page_end;
	}
}

sub print_page_start {
	print $query->header;
	print "<html>\n";
	print "<head>\n";
	print "<title>Email Form</title>\n";
	print "</head>\n";
	print "<body>\n";
	print "<h1>Email Form</h1>\n";
}

sub print_page_end {
	print "</body>\n";
	print "</html>\n";
}

sub print_form {
	print "<form method=\"post\">\n";
	print "<p>\nYour email address:\n";
	print "<input type\"text\" name=\"from\" />\n";
	print "</p>\n";
	print "<p>\nEmail subject:\n";
	print "<input type=\"text\" name=\"subject\" />\n";
	print "</p>\n";
	print "<textarea name=\"body\" wrap=\"physical\" rows=\"5\" ";
	print "cols=\"70\">";
	print $body;
	print "</textarea>\n</p>\n";
	print "<p>\n<input type=\"submit\" value=\"Send Email\"/>\n</p>\n";
	print "</form>\n";
}

sub validate_form {
	
	if (!$subject) {
		$error_message .= "<li>You need to enter a subject";
		$error_message .= "for your message.</li>\n";
	}

	if (!$from) {
		$error_message .= "<li>You need to specify a recipient for ";
		$error_message .= "the message.</li>\n";
	}
	if ($from !~ m/^[\w\.\-_]+\@[\w\.]+$/gi) {
		$error_message .= "<li>The email address you entered is invalid,";
		$error_message .= "please enter a valid address. </li>\n";
	}

	if (!$body) {
		$error_message .= "<li>You need to enter some text in the ";
		$error_message .= "body of your message.</li>\n";
	}	

	return $error_message;
}

sub print_error_message {
	print "<font color=\"red\">\n";
	print "<p>Please correct the following errors:</p>\n";
	print "<ul>\n";
	print $error_message;
	print "</ul>\n";
	print "</font>\n";
}

sub print_success {
	print "<p>An email with the subject \"$subject\" was sent to ";
	print "$address from $from.</p>\n";
}

sub send_email {
	my $sendmail = "/usr/lib/sendmail -n -t -oi";

	open(MAIL, "| $sendmail") or die "Couldn’t open sendmail: ";
	print MAIL "From: $from\n";
	print MAIL "To: $address\n";
	print MAIL "Subject: $subject\n";
	print MAIL "\n";
	print MAIL "$body\n";
	close MAIL;
}	


