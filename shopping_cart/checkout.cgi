#!/usr/bin/perl -w

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $query = CGI->new();

my $file = 'products.txt';
my $cart_file = '/tmp/cart.txt';
my ($session_id, $page_title, $name, $address, $city, $state,
	$zip, $cc_type, $cc_number, $exp_month, $exp_year);
my @user_cart;
my %cc_types = ('AMEX' => 'American Express',
				'VISA' => 'Visa',
				'MC' => 'Master Card', 
				'DISC' => 'Discovery');	

if ($query->cookie('session_id')) {
	$session_id = ($query->cookie('session_id'));
} else {
	$page_title = 'Checkout: Error';
	print_page_start();
	print_no_cart();
	print_page_end();
	#1t1r1i1f
	#exit;
}

get_cart_contents();

if (@user_cart) {
	if ($query->param('cc_type')) {
		set_variables();
		my $error_message = valid_form();
		if (!$error_message) {
			$page_title = "Checkout Complete";
			print_page_start();
			insert_order();
			empty_cart();
			print_success();
			print_page_end();
		} else {
			$page_title = "Checkout: Please correct errors";
			print_page_start();
			print_error($error_message);
			print_form();
			print_page_end();
		}
	} else {
		$page_title = "Checkout";
		print_page_start();
		print_form();
		print_page_end();
	}
} else {
	$page_title = "Error: Your cart is empty";
	print_page_start();
	print_no_cart();
	print_page_end();
}

sub print_page_start {
	print $query->header;
	print "<html>\n<head>\n<title>$page_title</title>\n";
	print "</head>\n<body>\n";
	print "<h1 align=\"center\">$page_title</h1>\n";
}

sub print_no_cart {
	print "<p>There are no items in your shopping cart.</p>\n";
}

sub print_page_end {
	print "<p><div align=\"center\"><b>";
	print "<a href=\"catalog.cgi\">return to catalog</a></b></div></p>\n";
	print "</body>\n</html>\n";
}

sub get_cart_contents {
	chdir;
	open (CART, '<', $cart_file) or die "Could not open '$cart_file' $!:";
	my @records = <CART>;
	@user_cart = ();

	foreach my $record (@records) {
		chomp $record;
		my ($rec_session, $rec_product_id, $rec_quantity) = split /:/, $record;

		if ($rec_session eq $session_id) {
			push @user_cart, $record;
		}
	}
}

sub set_variables {
	$name = $query->param('name');
	$address = $query->param('address');
	$city = $query->param('city');
	$state = $query->param('state');
	$zip = $query->param('zip');
	$cc_type = $query->param('cc_type');
	$cc_number = $query->param('cc_number');
	$exp_month = $query->param('exp_month');
	$exp_year = $query->param('exp_year');
}

sub valid_form {
	my $error_message;
	$error_message .= "<li>You must enter your name</li>\n" if ($name =~ /^\s*$/);
	$error_message .= "<li>You must enter your address</li>\n" if ($address =~ /^\s*$/);
	$error_message .= "<li>You must enter your city</li>\n" if ($city =~ /^\s*$/);
	$error_message .= "<li>You must enter a valid zip code</li>\n" if ($zip !~ /^\d+$/);
	$error_message .= "<li>You must enter a valid expiration month</li>" if ($exp_month > 12 || $exp_month < 1);
	$error_message .= "<li>You must enter a valid expiration year</li>\n" if ($exp_year < 2007 || $exp_year > 2017);
	$error_message .= "<li>You must enter a valid CC number</li>\n" if ($cc_number !~ /^\d+$/);
	return $error_message;
}

sub insert_order {
	1;
}

sub empty_cart {
	chdir;
	open (CART, '+<', $cart_file) or die "Could not open? '$cart_file' $!:";
	flock CART, 2;
	seek CART, 0, 0;
	my @records = <CART>;
	my @new_records = ();
	foreach my $record (@records) {
		chomp $record;
		my ($rec_session_id, $rec_product_id, $rec_quantity) = split /:/, $record;
		unless (($rec_session_id eq $session_id) and
			($rec_product_id eq $query->param('product_id'))) {
			push @new_records, $record . "\n";
		}
	}
	seek CART, 0, 0;
	truncate CART, 0;
	print CART @new_records;
	close CART;
}

sub print_success {
	print "<p>Your order is complete.</p>\n";
}

sub print_error {
	my $error_message = shift;
	
	print "<p>Please correct the following errors:</p>\n";
	
	if ($error_message) {
		print "<ul>\n$error_message\n</ul>\n";
	}
}

sub print_form {
	print "<form>\n";
	print "<table border=\"0\">\n";
	print "<tr><td>Name:</td>\n";
	print "<td><input type=\"text\" name=\"name\" value=\"$name\" />\n";
	print "</td></tr>\n";
	print "<tr><td>Street address:</td>\n";
	print "<td><input type=\"text\" name=\"address\" ";
	print "value=\"$address\" size=\"40\" maxlength=\"80\" />";
	print "</td></tr>\n";
	print "<tr><td>City:</td>\n";
	print "<td><input type=\"text\" name=\"city\" value=\"$city\" />";
	print "</td></tr>\n";
	print "<tr><td>State:</td>\n";
	print "<td><input type=\"text\" name=\"state\" ";
	print "value=\"$state\" size=\"2\" MAXLENGTH=\"2\" /></td></tr>\n";
	print "<tr><td>Zip:</td>\n";
	print "<td><input type=\"text\" name=\"zip\" ";
	print "value=\"$zip\" size=\"5\" maxlength=\"5\" /></td></tr>\n";
	print "<td>Credit card:</td>\n<td>\n<select name=\"cc_type\">\n";
	foreach my $key (sort {$a <=> $b} keys %cc_types) {
		print "<option value=\"$key\">", $cc_types{$key}, "</option>\n";
	}
	print "</select>\n</td>\n";
	print "</select>\n</td>\n";
	print "<tr><td>Credit card number:</td>\n";
	print "<td><input type=\"text\" name=\"cc_number\" ";
	print "value=\"$cc_number\"></td></tr>\n";
	print "<tr><td>Expiration date:</td>\n";
	print "<td><input type=\"text\" name=\"exp_month\" ";
	print "value=\"$exp_month\" size=\"2\" maxlength=\"2\">\n";
	print "<input type=\"text\" name=\"exp_year\" ";
	print "value=\"$exp_year\" size=\"2\" maxlength=\"4\"></tr>\n";
	print "<tr><td></td>\n";
	print "<td><input type=\"submit\" value=\"Complete Checkout\">";
	print "</td></tr>\n";
	print "</table>\n";
	print "</form>\n";
}	
